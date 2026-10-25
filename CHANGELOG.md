# Changelog

## [Unreleased]
- Replace the Ollama integration with a locally trained online-learning model
  that learns next-session returns from new Yahoo Finance price history.
- Persist per-ticker weights and walk-forward learning metrics locally.
- Refresh the local research interface with an Indonesian, data-focused design.
- Document the local learning workflow, update cadence, and data limitations.

## [0.1.0]
- Add an English-language stock analysis command using Yahoo Finance price data
  and a local Ollama model.
- Add one-time Python environment setup and document separate setup and daily
  usage commands.
- Improve retry behavior so the configured retry count is honored and the final
  failure is raised without an extra call.
- Use timezone-aware UTC timestamps for events and ingested records.
- Report Yahoo Finance fetch failures and malformed Ollama responses clearly.
- Add regression tests for stock analysis and core utilities.
- Initial project scaffold and import-safe package layout.
