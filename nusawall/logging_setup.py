from __future__ import annotations

import logging

LOGGER = logging.getLogger("nusawall")


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return LOGGER
