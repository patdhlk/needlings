"""Verify `ubc` is available; if not, print install instructions."""
from __future__ import annotations

import shutil

INSTALL_INSTRUCTIONS = (
    "ubc (the useblocks CLI) was not found on PATH.\n"
    "Install it from https://ubcode.useblocks.com/ubc/installation.html\n"
    "The devcontainer in this repo installs it automatically — consider using "
    "GitHub Codespaces for a zero-config setup."
)


def ensure_ubc() -> str:
    path = shutil.which("ubc")
    if path is None:
        raise RuntimeError(INSTALL_INSTRUCTIONS)
    return path
