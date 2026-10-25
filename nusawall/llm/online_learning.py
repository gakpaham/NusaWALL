from __future__ import annotations

import hashlib
import json
import math
import os
import threading
from pathlib import Path
from typing import TypedDict

from pandas import Series

from nusawall.paths import ARTIFACTS_DIR


FEATURE_COUNT = 6
LEARNING_RATE = 0.01
REGULARIZATION = 0.001
MAX_TARGET = 30.0
MAX_FEATURE = 10.0
MIN_TRAINING_SAMPLES = 20
_MODEL_LOCK = threading.Lock()


class LearningResult(TypedDict):
    prediction: float | None
    samples: int
    new_samples: int
    mae: float | None
    directional_accuracy: float | None
    trained_until: str | None


def _date_text(value) -> str:
    return value.date().isoformat() if hasattr(value, "date") else str(value)[:10]


def _feature_rows(closes: Series) -> list[tuple[str, list[float], float | None]]:
    values = [float(value) for value in closes]
    dates = list(closes.index)
    rows = []
    for index in range(20, len(values)):
        current = values[index]
        if current <= 0:
            continue
        one_day = (current / values[index - 1] - 1) * 100
        five_day = (current / values[index - 5] - 1) * 100
        twenty_day = (current / values[index - 20] - 1) * 100
        mean_20 = sum(values[index - 19 : index + 1]) / 20
        deviation_20 = (current / mean_20 - 1) * 100
        daily_returns = [
            (values[position] / values[position - 1] - 1) * 100
            for position in range(index - 19, index + 1)
            if values[position - 1] > 0
        ]
        if len(daily_returns) > 1:
            mean_return = sum(daily_returns) / len(daily_returns)
            volatility_20 = math.sqrt(
                sum((value - mean_return) ** 2 for value in daily_returns)
                / (len(daily_returns) - 1)
            ) * math.sqrt(252)
        else:
            volatility_20 = 0.0

        features = [
            1.0,
            max(-MAX_FEATURE, min(MAX_FEATURE, one_day / 5)),
            max(-MAX_FEATURE, min(MAX_FEATURE, five_day / 10)),
            max(-MAX_FEATURE, min(MAX_FEATURE, twenty_day / 20)),
            max(-MAX_FEATURE, min(MAX_FEATURE, deviation_20 / 10)),
            max(-MAX_FEATURE, min(MAX_FEATURE, volatility_20 / 100)),
        ]
        target = (
            (values[index + 1] / current - 1) * 100
            if index + 1 < len(values) and values[index + 1] > 0
            else None
        )
        rows.append((_date_text(dates[index]), features, target))
    return rows


def _new_state(ticker: str) -> dict:
    return {
        "version": 1,
        "ticker": ticker,
        "weights": [0.0] * FEATURE_COUNT,
        "last_trained_date": None,
        "samples": 0,
        "absolute_error_sum": 0.0,
        "directional_hits": 0,
    }


def _state_path(ticker: str) -> Path:
    key = hashlib.sha256(ticker.encode("utf-8")).hexdigest()[:24]
    return ARTIFACTS_DIR / "online_models" / f"{key}.json"


def _read_state(path: Path, ticker: str) -> dict:
    if not path.exists():
        return _new_state(ticker)
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Model belajar lokal {ticker} tidak dapat dibaca: {exc}") from exc
    if (
        not isinstance(state, dict)
        or state.get("version") != 1
        or state.get("ticker") != ticker
        or not isinstance(state.get("weights"), list)
        or len(state["weights"]) != FEATURE_COUNT
        or not all(isinstance(weight, (int, float)) and math.isfinite(weight) for weight in state["weights"])
        or not isinstance(state.get("samples"), int)
        or state["samples"] < 0
        or not isinstance(state.get("last_trained_date"), (str, type(None)))
        or not isinstance(state.get("absolute_error_sum"), (int, float))
        or not math.isfinite(state["absolute_error_sum"])
        or state["absolute_error_sum"] < 0
        or not isinstance(state.get("directional_hits"), int)
        or state["directional_hits"] < 0
        or state["directional_hits"] > state["samples"]
    ):
        raise RuntimeError(f"Format model belajar lokal {ticker} tidak valid.")
    return state


def _write_state(path: Path, state: dict) -> None:
    temporary_path = path.with_suffix(".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path.write_text(
            json.dumps(state, ensure_ascii=False, allow_nan=False),
            encoding="utf-8",
        )
        os.replace(temporary_path, path)
    except OSError as exc:
        raise RuntimeError(f"Model belajar lokal tidak dapat disimpan: {exc}") from exc
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def learn_and_predict(ticker: str, closes: Series) -> LearningResult:
    """Train on unseen next-session returns and persist a walk-forward linear model."""
    history = _feature_rows(closes)
    if not history:
        return {
            "prediction": None,
            "samples": 0,
            "new_samples": 0,
            "mae": None,
            "directional_accuracy": None,
            "trained_until": None,
        }

    model_path = _state_path(ticker)
    with _MODEL_LOCK:
        state = _read_state(model_path, ticker)
        last_trained_date = state["last_trained_date"]
        new_samples = 0
        weights = [float(weight) for weight in state["weights"]]
        for date, features, target in history:
            if target is None or (last_trained_date and date <= last_trained_date):
                continue

            prediction = max(
                -MAX_TARGET,
                min(MAX_TARGET, sum(weight * feature for weight, feature in zip(weights, features))),
            )
            error = max(-MAX_TARGET, min(MAX_TARGET, target)) - prediction
            for index, feature in enumerate(features):
                penalty = 0.0 if index == 0 else REGULARIZATION * weights[index]
                weights[index] += LEARNING_RATE * (error * feature - penalty)
            state["samples"] += 1
            state["absolute_error_sum"] += abs(target - prediction)
            if (target >= 0) == (prediction >= 0):
                state["directional_hits"] += 1
            state["last_trained_date"] = date
            new_samples += 1

        state["weights"] = weights
        _write_state(model_path, state)

    latest_date, latest_features, _ = history[-1]
    prediction = max(
        -MAX_TARGET,
        min(MAX_TARGET, sum(weight * feature for weight, feature in zip(weights, latest_features))),
    )
    sample_count = state["samples"]
    return {
        "prediction": prediction if sample_count >= MIN_TRAINING_SAMPLES else None,
        "samples": sample_count,
        "new_samples": new_samples,
        "mae": state["absolute_error_sum"] / sample_count if sample_count else None,
        "directional_accuracy": (
            state["directional_hits"] / sample_count * 100 if sample_count else None
        ),
        "trained_until": state["last_trained_date"] or latest_date,
    }
