"""Detect the 'I AM NOT DONE' sentinel in exercise files."""
from __future__ import annotations

from pathlib import Path

TEXT_SUFFIXES = {".rst", ".md", ".txt", ".toml", ".py", ".json"}


def is_still_not_done(root: Path, sentinel: str) -> bool:
    """Return True if any text file under `root` contains `sentinel`."""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if sentinel in path.read_text(encoding="utf-8", errors="ignore"):
                return True
        except OSError:
            continue
    return False
