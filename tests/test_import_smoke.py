from __future__ import annotations

import nusawall
from nusawall.constants import IDX_MARKETS


def test_import_smoke():
    assert nusawall.__version__
    assert "IDX" in IDX_MARKETS
