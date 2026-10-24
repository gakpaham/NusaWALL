from __future__ import annotations

import importlib

import nusawall


def test_package_imports():
    assert hasattr(nusawall, "__version__")
    assert importlib.import_module("nusawall.core").__name__ == "nusawall.core"
