from pathlib import Path

from needlings.paths import Paths


def test_paths_from_repo_root(tmp_path: Path) -> None:
    (tmp_path / "exercises").mkdir()
    (tmp_path / "exercises" / "_base").mkdir()

    paths = Paths.from_root(tmp_path)

    assert paths.root == tmp_path
    assert paths.exercises == tmp_path / "exercises"
    assert paths.base == tmp_path / "exercises" / "_base"
    assert paths.state_dir == tmp_path / ".needlings"
    assert paths.state_file == tmp_path / ".needlings" / "state.json"
    assert paths.crash_dir == tmp_path / ".needlings" / "crashes"


def test_paths_discover_walks_up(tmp_path: Path) -> None:
    (tmp_path / "exercises").mkdir()
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)

    paths = Paths.discover(start=nested)

    assert paths.root == tmp_path


def test_paths_discover_raises_when_not_found(tmp_path: Path) -> None:
    import pytest

    with pytest.raises(RuntimeError, match="not inside a needlings"):
        Paths.discover(start=tmp_path)
