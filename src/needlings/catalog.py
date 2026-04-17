"""Discover and load exercise chapters from disk."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from needlings.models import Assertion, Chapter, Exercise, ExerciseId, VerifyConfig
from needlings.paths import Paths


def load_catalog(paths: Paths) -> list[Chapter]:
    """Walk `exercises/`, return ordered list of chapters with their exercises."""
    chapters: list[Chapter] = []
    for chapter_dir in sorted(paths.exercises.iterdir()):
        if not chapter_dir.is_dir() or chapter_dir.name.startswith("_"):
            continue
        chapters.append(_load_chapter(chapter_dir))
    return chapters


def _load_chapter(chapter_dir: Path) -> Chapter:
    index_file = chapter_dir / "index.toml"
    if not index_file.exists():
        raise RuntimeError(f"Missing {index_file} — each chapter needs an index.toml.")

    data = tomllib.loads(index_file.read_text())
    title = data.get("title", chapter_dir.name)
    slugs: list[str] = data.get("exercises", [])

    exercises: list[Exercise] = []
    for slug in slugs:
        ex_dir = chapter_dir / slug
        if not ex_dir.is_dir():
            raise RuntimeError(
                f"Chapter {chapter_dir.name} references {slug!r} in index.toml "
                f"but the directory does not exist."
            )
        exercises.append(_load_exercise(chapter_dir.name, slug, ex_dir))

    return Chapter(id=chapter_dir.name, title=title, exercises=exercises)


def _load_exercise(chapter_id: str, slug: str, ex_dir: Path) -> Exercise:
    info_file = ex_dir / "info.toml"
    if not info_file.exists():
        raise RuntimeError(f"Missing {info_file}.")

    data: dict[str, Any] = tomllib.loads(info_file.read_text())
    verify_raw = data.get("verify", {})
    backend = verify_raw.get("backend", "sphinx")
    backends = backend if isinstance(backend, list) else [backend]

    assertions = [
        Assertion(type=a["type"], params={k: v for k, v in a.items() if k != "type"})
        for a in verify_raw.get("assertions", [])
    ]

    verify = VerifyConfig(
        backend=backends,
        flags=list(verify_raw.get("flags", [])),
        assertions=assertions,
    )

    return Exercise(
        id=ExerciseId(chapter=chapter_id, slug=slug),
        name=data["name"],
        order=int(data.get("order", 0)),
        hint=data.get("hint", ""),
        sentinel=data.get("sentinel", ".. I AM NOT DONE"),
        verify=verify,
        path=str(ex_dir),
    )


def flatten(catalog: list[Chapter]) -> list[Exercise]:
    """Return a flat, ordered list of exercises."""
    return [ex for ch in catalog for ex in ch.exercises]
