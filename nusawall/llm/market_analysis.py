from __future__ import annotations

import math

from pandas import DataFrame, Series
import yfinance as yf

from nusawall.llm.online_learning import MIN_TRAINING_SAMPLES, learn_and_predict


DEFAULT_QUESTION = (
    "Analisis tren harga, risiko yang terlihat, dan hal yang perlu dipantau berikutnya."
)
ANALYTICS_ENGINE = "NusaWall Online Learner"


def _fetch_history(ticker: str, period: str) -> tuple[str, DataFrame, Series]:
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("Ticker tidak boleh kosong.")

    try:
        history = yf.Ticker(symbol).history(period=period, interval="1d", auto_adjust=True)
    except yf.exceptions.YFException as exc:
        raise RuntimeError(f"Yahoo Finance gagal mengambil data {symbol}: {exc}") from exc
    if history.empty:
        raise ValueError(
            f"Tidak ada data harga untuk {symbol}. Periksa ticker (misalnya BBCA.JK "
            "untuk saham BEI) atau coba periode lain."
        )
    if "Close" not in history.columns:
        raise ValueError(f"Data harga {symbol} tidak memiliki kolom Close.")

    closes = history["Close"].dropna()
    if closes.empty:
        raise ValueError(f"Harga penutupan {symbol} tidak tersedia.")
    return symbol, history, closes


def _show(value: float, suffix: str = "") -> str:
    return f"{value:,.2f}{suffix}" if math.isfinite(value) else "tidak tersedia"


def fetch_market_data(ticker: str, period: str = "6mo") -> tuple[str, str]:
    """Fetch recent daily prices and summarize them for the native analytics engine."""
    symbol, history, closes = _fetch_history(ticker, period)

    first_close = float(closes.iloc[0])
    last_close = float(closes.iloc[-1])
    period_return = ((last_close / first_close) - 1) * 100 if first_close else 0.0
    high = float(history["High"].max()) if "High" in history else float("nan")
    low = float(history["Low"].min()) if "Low" in history else float("nan")
    latest_volume = (
        float(history["Volume"].iloc[-1])
        if "Volume" in history and not history["Volume"].empty
        else float("nan")
    )
    daily_returns = closes.pct_change().dropna()
    annualized_volatility = (
        float(daily_returns.std() * math.sqrt(252) * 100)
        if len(daily_returns) > 1
        else float("nan")
    )

    summary = "\n".join(
        [
            f"Ticker: {symbol}",
            f"Data period: {history.index[0].date()} to {history.index[-1].date()}",
            f"Trading sessions: {len(history)}",
            f"First closing price: {_show(first_close)}",
            f"Latest closing price: {_show(last_close)}",
            f"Price change over period: {_show(period_return, '%')}",
            f"Period high: {_show(high)}",
            f"Period low: {_show(low)}",
            f"Latest session volume: {_show(latest_volume)}",
            f"Estimated historical annualized volatility: {_show(annualized_volatility, '%')}",
        ]
    )

    rows = ["Date | Close | High | Low | Volume"]
    for date, row in history.tail(10).iterrows():
        values = []
        for column in ("Close", "High", "Low", "Volume"):
            value = float(row[column]) if column in row else float("nan")
            values.append(_show(value) if math.isfinite(value) else "N/A")
        rows.append(f"{date.date().isoformat()} | " + " | ".join(values))

    return summary, "\n".join(rows)


def _format_analysis(
    ticker: str,
    question: str,
    period: str,
    history: DataFrame,
    closes: Series,
    learning: dict,
) -> str:
    first_close = float(closes.iloc[0])
    latest_close = float(closes.iloc[-1])
    period_change = (latest_close / first_close - 1) * 100 if first_close else 0.0
    short_start = float(closes.iloc[max(0, len(closes) - 21)])
    recent_change = (latest_close / short_start - 1) * 100 if short_start else 0.0
    sma20 = float(closes.tail(20).mean()) if len(closes) >= 20 else float("nan")
    sma50 = float(closes.tail(50).mean()) if len(closes) >= 50 else float("nan")
    daily_returns = closes.pct_change().dropna()
    volatility = (
        float(daily_returns.std() * math.sqrt(252) * 100)
        if len(daily_returns) > 1
        else float("nan")
    )
    drawdown = float((closes / closes.cummax() - 1).min() * 100)
    latest_volume = (
        float(history["Volume"].dropna().iloc[-1])
        if "Volume" in history and not history["Volume"].dropna().empty
        else float("nan")
    )
    average_volume = (
        float(history["Volume"].dropna().tail(20).mean())
        if "Volume" in history and not history["Volume"].dropna().empty
        else float("nan")
    )

    has_both_averages = math.isfinite(sma20) and math.isfinite(sma50)
    if has_both_averages and latest_close > sma20 and latest_close > sma50:
        trend_read = "Harga terakhir berada di atas rata-rata 20 dan 50 sesi."
    elif has_both_averages and latest_close < sma20 and latest_close < sma50:
        trend_read = "Harga terakhir berada di bawah rata-rata 20 dan 50 sesi."
    elif not has_both_averages:
        trend_read = "Data historis belum mencakup 20 atau 50 sesi untuk perbandingan rata-rata."
    else:
        trend_read = "Posisi harga terhadap rata-rata 20 dan 50 sesi belum searah."

    risk_read = (
        f"Volatilitas historis tahunan diperkirakan {_show(volatility, '%')}; "
        f"penurunan maksimum dari puncak ke titik terendah pada periode ini "
        f"{_show(abs(drawdown), '%')}."
    )
    if math.isfinite(latest_volume) and math.isfinite(average_volume) and average_volume > 0:
        volume_read = (
            f"Volume sesi terakhir {_show(latest_volume)} saham, "
            f"{latest_volume / average_volume:.2f}× rata-rata 20 sesi "
            f"({_show(average_volume)} saham)."
        )
    else:
        volume_read = "Data volume yang memadai tidak tersedia untuk dibandingkan."

    monitor = []
    if math.isfinite(sma20):
        if latest_close < sma20:
            monitor.append("apakah harga mampu kembali ke atas rata-rata 20 sesi")
        else:
            monitor.append("apakah harga bertahan di atas rata-rata 20 sesi")
    if math.isfinite(sma50) and latest_close < sma50:
        monitor.append("perubahan posisi terhadap rata-rata 50 sesi")
    if math.isfinite(latest_volume) and math.isfinite(average_volume) and average_volume > 0:
        if latest_volume > average_volume * 1.5:
            monitor.append("lonjakan volume dan arah pergerakan harga berikutnya")
        elif latest_volume < average_volume * 0.5:
            monitor.append("volume yang masih jauh di bawah rata-rata")
    monitor.append("risiko berita, fundamental, dan kondisi pasar yang tidak tercakup data harga")

    if learning["prediction"] is None:
        learning_read = (
            f"Model sudah mencatat {learning['samples']} contoh; dibutuhkan minimal "
            f"{MIN_TRAINING_SAMPLES} contoh berlabel untuk menampilkan estimasi."
        )
    else:
        direction = "positif" if learning["prediction"] >= 0 else "negatif"
        learning_read = (
            f"Estimasi perubahan sesi berikutnya {_show(learning['prediction'], '%')} "
            f"({direction}); model telah belajar dari {learning['samples']} pasangan sesi "
            f"dan menambahkan {learning['new_samples']} pasangan data baru pada permintaan ini."
        )
        if learning["mae"] is not None:
            learning_read += (
                f" Galat absolut rata-rata evaluasi berurutan "
                f"{_show(learning['mae'], '%')} dan kecocokan arah "
                f"{_show(learning['directional_accuracy'], '%')}."
            )
        learning_read += (
            " Metrik adalah evaluasi historis berurutan dan bukan jaminan akurasi ke depan."
        )

    focus = question.casefold()
    if any(word in focus for word in ("risiko", "risk", "volatil", "drawdown", "turun")):
        focus_insight = risk_read
    elif any(word in focus for word in ("volume", "transaksi", "likuid")):
        focus_insight = volume_read
    elif any(word in focus for word in ("tren", "trend", "harga", "price", "return", "naik")):
        focus_insight = trend_read
    else:
        focus_insight = (
            f"Perubahan harga periode ini {_show(period_change, '%')}; "
            f"perubahan sekitar 20 sesi terakhir {_show(recent_change, '%')}."
        )

    return "\n\n".join(
        [
            f"Ringkasan\n{ticker} berubah {_show(period_change, '%')} selama "
            f"{len(history)} sesi perdagangan ({history.index[0].date()}–{history.index[-1].date()}). "
            f"Harga penutupan terakhir {_show(latest_close)}.",
            f"Tren\n{trend_read} Perubahan dalam sekitar 20 sesi terakhir "
            f"{_show(recent_change, '%')}; rata-rata 20 sesi {_show(sma20)} "
            f"dan rata-rata 50 sesi {_show(sma50)}.",
            f"Risiko\n{risk_read} Volatilitas dan penurunan historis bukan ukuran pasti "
            "risiko atau jaminan pergerakan selanjutnya.",
            f"Volume\n{volume_read}",
            f"Fokus pertanyaan\n{question.strip()}",
            f"Indikator terkait fokus\n{focus_insight}",
            f"Model belajar lokal\n{learning_read}",
            f"Yang perlu dipantau\n" + "; ".join(monitor) + ".",
            f"Metode\nModel regresi linear online NusaWall dilatih bertahap dari pasangan "
            f"indikator dan return sesi berikutnya pada data historis {period}. Bobot dan "
            "tanggal belajar terakhir disimpan lokal di folder artifacts. Data berita, "
            "fundamental, likuiditas, dan aksi korporasi tidak dianalisis.",
        ]
    )


def analyze_stock(
    ticker: str,
    *,
    question: str = DEFAULT_QUESTION,
    period: str = "6mo",
) -> str:
    symbol, history, closes = _fetch_history(ticker, period)
    learning = learn_and_predict(symbol, closes)
    return _format_analysis(symbol, question, period, history, closes, learning)
