# NusaWall

**Local market research for Indonesian and U.S. equities.**

NusaWall is a Python research toolkit for market data ingestion, feature
engineering, and stock analysis. Its browser interface trains a small,
incremental prediction model in-house from historical prices provided by
Yahoo Finance. It does not call another AI service or download a pretrained AI
model.

> **Disclaimer:** NusaWall is a research and educational tool. Its analysis may
> be incomplete or inaccurate and is not investment advice, a recommendation,
> or a guarantee of future performance.

## Highlights

- Analyze IDX and U.S. stock tickers from a local web interface or the command
  line.
- Train a local online-learning model on historical price features and
  next-session returns.
- Review the model's next-session estimate alongside price trends, volatility,
  drawdown, and recent trading volume.
- Keep model weights on the computer in `artifacts/online_models/`; each
  observed session is added to training only once.
- Explore modular components for ingestion, market features, evaluation, and
  research workflows.

Yahoo Finance data retrieval requires an internet connection. The model
implementation is included in the project and trains locally; it is not a
chatbot or a generative language model. It learns from historical daily
prices when an analysis is requested and new labeled data is available.
Learning is not a real-time streaming process. Python dependencies still need
to be installed for a fresh setup.

## Requirements

- Python 3.10 or later
- An internet connection to retrieve market data from Yahoo Finance

## Quick start

### 1. Set up the Python environment

From the repository root, run:

```powershell
python manage.py setup
```

This creates the project `.venv` environment and installs NusaWall's Python
dependencies. Setup is normally required only once. No separate AI software,
AI service, or pretrained model download is needed.

### 2. Start the web app

On Windows, run:

```powershell
.\.venv\Scripts\python.exe manage.py web
```

On macOS or Linux, run:

```bash
.venv/bin/python manage.py web
```

Keep the terminal open while using the app. Then visit
[http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

### 3. Analyze a stock

Enter a ticker such as `BBCA.JK` or `AAPL`, select a historical period, and
submit a focus for the analysis. IDX tickers generally use the `.JK` suffix.
The app fetches daily price history from Yahoo Finance, incrementally trains
the local model when new sessions are available, and reports its estimate with
the underlying indicators.

To stop the web server, focus its terminal and press **Ctrl+C**.

## Command-line usage

The CLI uses the same analysis workflow without starting the browser app.

### Windows

```powershell
.\.venv\Scripts\python.exe manage.py analyze BBCA.JK
.\.venv\Scripts\python.exe manage.py analyze AAPL --period 1y
.\.venv\Scripts\python.exe manage.py analyze AAPL --question "Tinjau tren dan volatilitas harga"
```

### macOS and Linux

```bash
.venv/bin/python manage.py analyze BBCA.JK
.venv/bin/python manage.py analyze AAPL --period 1y
```

The default history period is `6mo`. For available commands and options:

```powershell
.\.venv\Scripts\python.exe manage.py --help
.\.venv\Scripts\python.exe manage.py analyze --help
```

## Configuration

The web server listens on `127.0.0.1:8000` by default, making it available
only on the local computer. To choose a different host or port:

```powershell
.\.venv\Scripts\python.exe manage.py web --host 127.0.0.1 --port 8001
```

Only bind to another host when you understand the network exposure that
creates.

## How learning and analysis work

1. NusaWall retrieves daily, auto-adjusted price history for the requested
   ticker and period from Yahoo Finance using `yfinance`.
2. A local linear model creates features from recent returns, moving-average
   distance, and volatility. It learns to estimate the following session's
   return from historical examples, processing observations chronologically
   to avoid training on future labels.
3. Newly completed sessions update the model once per ticker. Weights,
   sample counts, and walk-forward evaluation statistics are stored in
   `artifacts/online_models/` and reused on the next analysis.
4. NusaWall reports the model estimate alongside period changes, 20- and
   50-session moving averages, historical volatility, maximum drawdown, and
   recent volume. The report is assembled locally; no prompt is sent to a
   language model.

The analysis covers historical prices only. It does not automatically
incorporate news, company filings, fundamentals, or other sources. Historical
performance is not a guarantee of future accuracy. The model is intentionally
simple, may perform poorly, and does not make investment recommendations;
verify important information independently. Stored models can be removed by
deleting their files under `artifacts/online_models/`.
At least 20 completed training examples are required before a model estimate
is shown.

## Project structure

```text
NusaWall/
├── nusawall/
│   ├── configs/       # Configuration and feature schemas
│   ├── core/          # Shared utilities and infrastructure
│   ├── features/      # Technical, fundamental, macro, and market features
│   ├── ingestion/     # Market data and information-source connectors
│   ├── llm/           # Market analysis workflow and built-in analytics
│   ├── market/        # Market calendars and corporate actions
│   ├── serving/       # Serving components
│   └── web/           # Local browser interface
├── docs/              # Architecture, policies, and operational guides
├── tests/             # Unit, smoke, and architecture tests
├── manage.py          # Project command-line entry point
└── pyproject.toml     # Package metadata and dependencies
```

See the [architecture overview](docs/architecture/overview.md) for additional
implementation details.

## Development

Run the test suite from the repository root:

```powershell
python -m pytest
```

Check the Python environment:

```powershell
.\.venv\Scripts\python.exe manage.py doctor
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance and
[CHANGELOG.md](CHANGELOG.md) for project history.

## License

See [LICENSE](LICENSE) for the terms that apply to this project.
