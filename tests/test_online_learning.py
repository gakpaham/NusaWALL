from __future__ import annotations

import json

import pandas as pd
import pytest

from nusawall.llm import online_learning


def price_series(count: int = 65) -> pd.Series:
    dates = pd.date_range("2026-01-01", periods=count, freq="B")
    prices = [100 + index * 0.25 + (index % 4) * 0.08 for index in range(count)]
    return pd.Series(prices, index=dates)


def test_online_model_learns_new_sessions_once_and_persists(tmp_path, monkeypatch):
    monkeypatch.setattr(online_learning, "ARTIFACTS_DIR", tmp_path)
    prices = price_series()

    first = online_learning.learn_and_predict("BBCA.JK", prices)
    repeated = online_learning.learn_and_predict("BBCA.JK", prices)

    assert first["samples"] == 44
    assert first["new_samples"] == 44
    assert first["prediction"] is not None
    assert first["mae"] is not None
    assert repeated["samples"] == 44
    assert repeated["new_samples"] == 0
    assert repeated["prediction"] == first["prediction"]
    model_file = next((tmp_path / "online_models").glob("*.json"))
    initial_weights = json.loads(model_file.read_text(encoding="utf-8"))["weights"]

    updated = online_learning.learn_and_predict("BBCA.JK", price_series(66))

    assert updated["samples"] == 45
    assert updated["new_samples"] == 1
    assert updated["trained_until"] == "2026-04-01"
    saved_state = json.loads(model_file.read_text(encoding="utf-8"))
    assert saved_state["ticker"] == "BBCA.JK"
    assert saved_state["samples"] == 45
    assert len(saved_state["weights"]) == online_learning.FEATURE_COUNT
    assert saved_state["weights"] != initial_weights


def test_online_model_requires_twenty_one_closes_before_training(tmp_path, monkeypatch):
    monkeypatch.setattr(online_learning, "ARTIFACTS_DIR", tmp_path)

    result = online_learning.learn_and_predict("AAPL", price_series(20))

    assert result == {
        "prediction": None,
        "samples": 0,
        "new_samples": 0,
        "mae": None,
        "directional_accuracy": None,
        "trained_until": None,
    }


def test_online_model_rejects_corrupt_saved_state(tmp_path, monkeypatch):
    monkeypatch.setattr(online_learning, "ARTIFACTS_DIR", tmp_path)
    model_path = online_learning._state_path("AAPL")
    model_path.parent.mkdir(parents=True)
    model_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(RuntimeError, match="tidak dapat dibaca"):
        online_learning.learn_and_predict("AAPL", price_series())
