from pathlib import Path

from needlings.sentinel import is_still_not_done


def test_sentinel_detected(tmp_path: Path) -> None:
    (tmp_path / "a.rst").write_text("hello\n.. I AM NOT DONE\nworld\n")
    assert is_still_not_done(tmp_path, ".. I AM NOT DONE") is True


def test_sentinel_absent_when_removed(tmp_path: Path) -> None:
    (tmp_path / "a.rst").write_text("hello world\n")
    assert is_still_not_done(tmp_path, ".. I AM NOT DONE") is False


def test_sentinel_searches_recursively(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.rst").write_text(".. I AM NOT DONE\n")
    assert is_still_not_done(tmp_path, ".. I AM NOT DONE") is True


def test_sentinel_ignores_non_text(tmp_path: Path) -> None:
    (tmp_path / "img.bin").write_bytes(b"\x00\x01\x02")
    (tmp_path / "a.rst").write_text("nothing here")
    assert is_still_not_done(tmp_path, ".. I AM NOT DONE") is False


def test_sentinel_skips_pristine_snapshot(tmp_path: Path) -> None:
    # Learner has removed the sentinel from the live file.
    (tmp_path / "a.rst").write_text("done\n")
    # The pristine snapshot still carries it — that must not count as 'not done'.
    pristine = tmp_path / ".pristine"
    pristine.mkdir()
    (pristine / "a.rst").write_text(".. I AM NOT DONE\n")
    assert is_still_not_done(tmp_path, ".. I AM NOT DONE") is False
