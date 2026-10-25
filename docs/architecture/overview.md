# Architecture overview

NusaWall is a modular Python research toolkit. Market data ingestion, feature
engineering, evaluation, and serving code live in separate package areas under
`nusawall/`.

## Built-in market analysis

The `manage.py analyze` command calls `nusawall.llm.market_analysis`:

1. `_fetch_history` requests daily, auto-adjusted price history for the
   requested ticker and period from Yahoo Finance using `yfinance`.
2. `learn_and_predict` in `nusawall.llm.online_learning` builds daily features
   from returns, moving-average distance, and volatility. It trains a linear
   model in chronological order to estimate the next-session return.
3. Each ticker's weights, training date, and walk-forward error metrics are
   stored in `artifacts/online_models/`. On later analyses, only newly
   completed observations are added, once each. Learning runs when analysis is
   requested and new Yahoo Finance data is available; it is not real-time
   streaming.
4. `_format_analysis` combines the model estimate with period and recent
   returns, 20- and 50-session moving averages, annualized historical
   volatility, maximum drawdown, and recent volume relative to its 20-session
   average.

Yahoo Finance access requires an internet connection. The analysis only covers
historical prices; it does not currently incorporate news, company filings, or
other sources. This is a small locally trained prediction model, not a
generative AI/chat model; its estimates are informational and are not
financial advice or guarantees of future performance.

## Local browser interface

Run `python manage.py web` to start the browser interface on
`http://127.0.0.1:8000`. The standard-library HTTP server serves the static
files in `nusawall/web/static/` and accepts JSON analysis requests at
`POST /api/analyze`. The endpoint validates request size and fields before
calling the same `analyze_stock` function used by the CLI. The server binds to
loopback by default. Market data still requires internet access.

## Development checks

Run the test suite from the repository root with:

```powershell
python -m pytest
```
