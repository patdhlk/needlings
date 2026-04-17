from pathlib import Path

from click.testing import CliRunner

from needlings.cli import cli
from tests.unit.test_catalog import _scaffold


def test_progress_shows_counts(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["--root", str(tmp_path), "progress"])
    assert result.exit_code == 0, result.output
    assert "0 / 2" in result.output or "0/2" in result.output


def test_progress_with_missing_root_shows_clean_error(tmp_path: Path) -> None:
    # Empty dir — no exercises/, no ubproject.toml — Paths.from_root will fail
    empty = tmp_path / "empty"
    empty.mkdir()
    runner = CliRunner()
    result = runner.invoke(cli, ["--root", str(empty), "progress"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_progress_with_malformed_catalog_shows_clean_error(tmp_path: Path) -> None:
    # exercises/ exists but contains a broken chapter that references missing exercise.
    ex = tmp_path / "exercises"
    ex.mkdir()
    (ex / "_base").mkdir()
    ch = ex / "01-setup"
    ch.mkdir()
    # index.toml references an exercise that doesn't exist
    (ch / "index.toml").write_text('title = "Setup"\nexercises = ["ex-1"]\n')

    runner = CliRunner()
    result = runner.invoke(cli, ["--root", str(tmp_path), "progress"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
