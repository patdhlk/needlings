from pathlib import Path

import pytest

from needlings.catalog import load_catalog
from needlings.paths import Paths


def _scaffold(tmp_path: Path) -> Paths:
    ex = tmp_path / "exercises"
    ex.mkdir()
    (ex / "_base").mkdir()
    ch = ex / "01-setup"
    ch.mkdir()
    (ch / "index.toml").write_text(
        'title = "Setup"\nexercises = ["01-hello", "02-ids"]\n'
    )

    for i, slug in enumerate(["01-hello", "02-ids"], start=1):
        d = ch / slug
        d.mkdir()
        (d / "starter").mkdir()
        (d / "starter" / "index.rst").write_text(".. I AM NOT DONE\n")
        (d / "solution").mkdir()
        (d / "solution" / "index.rst").write_text(".. req:: hi\n")
        (d / "info.toml").write_text(
            f"""
name = "Ex {i}"
chapter = "01-setup"
order = {i}
hint = "hint {i}"
sentinel = ".. I AM NOT DONE"

[verify]
backend = "sphinx"
flags = ["-W"]
"""
        )
    return Paths.from_root(tmp_path)


def test_load_catalog_returns_ordered_chapters(tmp_path: Path) -> None:
    paths = _scaffold(tmp_path)
    catalog = load_catalog(paths)

    assert [c.id for c in catalog] == ["01-setup"]
    assert catalog[0].title == "Setup"
    assert [e.id.slug for e in catalog[0].exercises] == ["01-hello", "02-ids"]
    assert catalog[0].exercises[0].name == "Ex 1"
    assert catalog[0].exercises[0].verify.backend == ["sphinx"]
    assert catalog[0].exercises[0].verify.flags == ["-W"]


def test_load_catalog_errors_on_missing_info(tmp_path: Path) -> None:
    paths = _scaffold(tmp_path)
    (paths.exercises / "01-setup" / "01-hello" / "info.toml").unlink()
    with pytest.raises(RuntimeError, match="info.toml"):
        load_catalog(paths)


def test_load_catalog_errors_on_unknown_slug_in_index(tmp_path: Path) -> None:
    paths = _scaffold(tmp_path)
    idx = paths.exercises / "01-setup" / "index.toml"
    idx.write_text('title = "Setup"\nexercises = ["01-hello", "03-missing"]\n')
    with pytest.raises(RuntimeError, match="03-missing"):
        load_catalog(paths)
