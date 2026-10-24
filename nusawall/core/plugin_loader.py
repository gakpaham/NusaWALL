from __future__ import annotations

import importlib


def load_plugin(module_path: str, attribute: str):
    module = importlib.import_module(module_path)
    return getattr(module, attribute)
