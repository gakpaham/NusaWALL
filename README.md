# NusaWall

NusaWall is a Python-based research scaffold for bilingual market intelligence and continual learning across Indonesian (IDX) and US financial markets. The project is designed to support data ingestion, feature engineering, evaluation workflows, and deployment-ready architecture for research and experimentation in quantitative finance and market intelligence.

## Overview

This repository provides a structured foundation for building ML-driven market intelligence systems, combining:

- market and macro data ingestion
- text/news signal extraction
- feature engineering for technical, fundamental, and microstructure domains
- point-in-time data handling and validation patterns
- model training, evaluation, and serving scaffolding

The project is intentionally structured as a research-oriented platform rather than a single-purpose script, making it suitable for experimentation, iteration, and extension as the system grows.

## Why NusaWall

NusaWall is meant to help teams work with both Indonesian and US market data in a unified workflow. It is especially useful for projects involving:

- equity market analysis
- macro and sentiment research
- news and event-driven signals
- factor and feature development
- research pipelines for LLM-assisted analysis

## Core Capabilities

- Data ingestion framework for market, macro, and news sources
- Feature modules for technical, fundamental, macro, microstructure, and text signal analysis
- Market calendar and exchange-aware logic for IDX and US instruments
- Research-oriented model and training scaffolding
- Deployment and serving skeletons for downstream consumption
- Configuration and registry patterns for extensible project architecture

## Repository Structure

```text
NusaWall/
├── nusawall/                  # Core package
│   ├── configs/               # Configuration and schema definitions
│   ├── core/                  # Shared utilities, registries, clocks, caching
│   ├── datasets/              # Dataset pipelines and structures
│   ├── features/              # Technical, fundamental, macro, microstructure
│   ├── ingestion/             # Source-specific ingestion modules
│   ├── market/                # Exchange, sectors, calendars, instruments
│   ├── text/                  # Text pipelines and deduplication
│   ├── monitoring/            # Monitoring and observability stubs
│   ├── serving/               # Serving layer scaffolding
│   ├── constants.py           # Shared market constants
│   └── version.py             # Package version
├── docs/                     # Project documentation and notes
├── scripts/                  # Project automation scripts
├── tests/                    # Smoke and architecture tests
├── manage.py                 # Minimal project CLI
├── pyproject.toml            # Python package metadata and dependencies
├── README.md                 # Project overview and documentation
├── CONTRIBUTING.md           # Contributor guidelines
├── LICENSE                   # License
└── ...
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- pip
- Git

### Installation

```bash
git clone https://github.com/gakpaham/NusaWALL.git
cd NusaWALL
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -r requirements/base.txt
```

If you are working in editable package mode:

```bash
pip install -e .
```

### One-Command Setup

Cukup jalankan satu perintah berikut dari root repository:

```bash
python manage.py
```

Perintah ini akan secara otomatis:

- membuat virtual environment `.venv` bila belum ada
- mengupgrade `pip`
- menginstal project dalam mode editable (`pip install -e .`)
- menyiapkan environment agar project siap dipakai

Setelah itu, Anda bisa mengecek kesehatan project dengan:

```bash
python manage.py doctor
```

### Run Tests

```bash
pytest
```

Atau jika Anda ingin bootstrap eksplisit:

```bash
python manage.py setup
```

## Development Notes

NusaWall is designed with a modular structure so each subsystem can evolve independently. This makes it easier to:

- add new data sources
- define custom feature pipelines
- test architecture boundaries
- iterate on research workflows without coupling modules tightly

The repository currently provides a strong scaffold and a set of foundational patterns, and is ready to be extended for production-grade experimentation.

## Contributing

Contributions are welcome. Please follow the repository’s contribution guidance in [CONTRIBUTING.md](CONTRIBUTING.md).

Before submitting changes, make sure the project remains stable by running the relevant validation checks and maintaining clear module boundaries.

## License

This project is licensed under the terms described in [LICENSE](LICENSE).

## Status

This project is currently in a research and scaffolding phase. It is structured for extensibility, but not every subsystem is intended to be fully production-hardened yet.

## Contact

For project discussions, issues, and contributions, please use the repository’s GitHub issue tracker and pull request workflow.

