from __future__ import annotations

import nox


@nox.session
def tests(session):
    session.install("-e", ".")
    session.run("pytest", "-q")
