from pathlib import Path

import pytest

from needlings.catalog import load_catalog
from needlings.paths import Paths


def _scaffold(tmp_path: Path, backend_as_list: bool = False, drop_name: bool = False, drop_assertion_type: bool = False) -> Paths:
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

        name_line = "" if drop_name else f'name = "Ex {i}"\n'

        backend_line = 'backend = ["sphinx", "assertions"]' if backend_as_list else 'backend = "sphinx"'

        assertions_section = ""
        if drop_assertion_type:
            assertions_section = "\n[[verify.assertions]]\nparam = 'value'"

        (d / "info.toml").write_text(
            f"""{name_line}chapter = "01-setup"
order = {i}
hint = "hint {i}"
sentinel = ".. I AM NOT DONE"

[verify]
{backend_line}
flags = ["-W"]{assertions_section}
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


def test_load_catalog_backend_as_list(tmp_path: Path) -> None:
    """Test that backend as a list is correctly copied (not aliased)."""
    paths = _scaffold(tmp_path, backend_as_list=True)
    catalog1 = load_catalog(paths)

    assert catalog1[0].exercises[0].verify.backend == ["sphinx", "assertions"]
    assert len(catalog1[0].exercises[0].verify.backend) == 2

    # Mutate the first catalog's backend list
    catalog1[0].exercises[0].verify.backend.append("extra")

    # Reload and verify the new catalog is unaffected
    catalog2 = load_catalog(paths)
    assert catalog2[0].exercises[0].verify.backend == ["sphinx", "assertions"]
    assert len(catalog2[0].exercises[0].verify.backend) == 2


def test_load_catalog_errors_on_missing_name(tmp_path: Path) -> None:
    """Test that missing 'name' field raises RuntimeError with file context."""
    paths = _scaffold(tmp_path, drop_name=True)
    with pytest.raises(RuntimeError, match="name"):
        load_catalog(paths)


def test_load_catalog_errors_on_missing_assertion_type(tmp_path: Path) -> None:
    """Test that missing 'type' in assertion raises RuntimeError with file context."""
    paths = _scaffold(tmp_path, drop_assertion_type=True)
    with pytest.raises(RuntimeError, match="type"):
        load_catalog(paths)


def test_flatten(tmp_path: Path) -> None:
    """Test that flatten returns a flat list of exercises."""
    from needlings.catalog import flatten
    paths = _scaffold(tmp_path)
    catalog = load_catalog(paths)
    flat = flatten(catalog)

    assert len(flat) == 2
    assert flat[0].id.slug == "01-hello"
    assert flat[1].id.slug == "02-ids"
