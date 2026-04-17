"""Compose a Sphinx build directory from _base + exercise starter."""
from __future__ import annotations

import shutil
from pathlib import Path


def compose_build_dir(base: Path, starter: Path, out: Path) -> None:
    """Populate `out` with `base` overlaid by `starter`. `out` is wiped first."""
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    _copy_tree(base, out)
    _copy_tree(starter, out)


def _copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
