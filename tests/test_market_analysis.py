from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest

import manage
from nusawall.llm import market_analysis
from nusawall.llm import online_learning


def test_default_run_shows_commands_without_installing(capsys, monkeypatch):
    monkeypatch.setattr(
        manage,
        "install_project",
        lambda _: pytest.fail("the default command must not install dependencies"),
    )

    manage.cmd_run()

    output = capsys.readouterr().out
    assert "One-time Python setup: python manage.py setup" in output
    assert "Analyze a ticker:    python manage.py analyze AAPL" in output


def test_fetch_market_data_formats_summary(monkeypatch):
    dates = pd.date_range("2026-01-01", periods=3, freq="D")
    history = pd.DataFrame(
        {
            "Close": [100.0, 105.0, 110.0],
            "High": [101.0, 106.0, 111.0],
            "Low": [99.0, 104.0, 109.0],
            "Volume": [1000, 1500, 2000],
        },
        index=dates,
    )
    fake_ticker = MagicMock()
    fake_ticker.history.return_value = history
    monkeypatch.setattr(market_analysis.yf, "Ticker", MagicMock(return_value=fake_ticker))

    summary, prices = market_analysis.fetch_market_data(" bbca.jk ")

    assert "Ticker: BBCA.JK" in summary
    assert "Price change over period: 10.00%" in summary
    assert "2026-01-03 | 110.00 | 111.00 | 109.00 | 2,000.00" in prices
    fake_ticker.history.assert_called_once_with(period="6mo", interval="1d", auto_adjust=True)


def test_fetch_market_data_rejects_empty_history(monkeypatch):
    fake_ticker = MagicMock()
    fake_ticker.history.return_value = pd.DataFrame()
    monkeypatch.setattr(market_analysis.yf, "Ticker", MagicMock(return_value=fake_ticker))

    with pytest.raises(ValueError, match="Tidak ada data harga"):
        market_analysis.fetch_market_data("NOT-A-TICKER")


def test_fetch_market_data_reports_yahoo_api_errors(monkeypatch):
    fake_ticker = MagicMock()
    fake_ticker.history.side_effect = market_analysis.yf.exceptions.YFException("rate limited")
    monkeypatch.setattr(market_analysis.yf, "Ticker", MagicMock(return_value=fake_ticker))

    with pytest.raises(RuntimeError, match="Yahoo Finance gagal mengambil data"):
        market_analysis.fetch_market_data("AAPL")


def test_analyze_stock_composes_local_market_indicators(monkeypatch, tmp_path):
    dates = pd.date_range("2026-01-01", periods=60, freq="B")
    closes = [100.0 + index for index in range(60)]
    history = pd.DataFrame(
        {
            "Close": closes,
            "High": [value + 1 for value in closes],
            "Low": [value - 1 for value in closes],
            "Volume": [1000 + index * 10 for index in range(60)],
        },
        index=dates,
    )
    fake_ticker = MagicMock()
    fake_ticker.history.return_value = history
    monkeypatch.setattr(market_analysis.yf, "Ticker", MagicMock(return_value=fake_ticker))
    monkeypatch.setattr(online_learning, "ARTIFACTS_DIR", tmp_path)

    answer = market_analysis.analyze_stock(
        " bbca.jk ",
        question="Apa risiko volatilitasnya?",
        period="3mo",
    )

    assert "Ringkasan\nBBCA.JK berubah 59.00%" in answer
    assert "Tren\nHarga terakhir berada di atas rata-rata 20 dan 50 sesi." in answer
    assert "Risiko\nVolatilitas historis tahunan diperkirakan" in answer
    assert "Fokus pertanyaan\nApa risiko volatilitasnya?" in answer
    assert "Indikator terkait fokus\nVolatilitas historis tahunan diperkirakan" in answer
    assert "Model belajar lokal\nEstimasi perubahan sesi berikutnya" in answer
    assert "Model regresi linear online NusaWall" in answer
    fake_ticker.history.assert_called_once_with(period="3mo", interval="1d", auto_adjust=True)


def test_analyze_stock_does_not_claim_unavailable_moving_averages(monkeypatch, tmp_path):
    dates = pd.date_range("2026-01-01", periods=10, freq="B")
    history = pd.DataFrame({"Close": range(100, 110)}, index=dates)
    fake_ticker = MagicMock()
    fake_ticker.history.return_value = history
    monkeypatch.setattr(market_analysis.yf, "Ticker", MagicMock(return_value=fake_ticker))
    monkeypatch.setattr(online_learning, "ARTIFACTS_DIR", tmp_path)

    answer = market_analysis.analyze_stock("AAPL")

    assert "Data historis belum mencakup 20 atau 50 sesi" in answer
    assert "rata-rata 20 sesi tidak tersedia" in answer
    assert "rata-rata 50 sesi tidak tersedia" in answer
