from pathlib import Path

from click.testing import CliRunner

from needlings.cli import cli
from tests.unit.test_catalog import _scaffold  # reuse scaffold helper


def test_cli_list_shows_chapters(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["--root", str(tmp_path), "list"])
    assert result.exit_code == 0, result.output
    assert "Setup" in result.output
    assert "Ex 1" in result.output
    assert "Ex 2" in result.output


def test_cli_list_with_missing_root_dir_shows_clean_error(tmp_path: Path) -> None:
    # tmp_path has no exercises/ — Paths.discover raises RuntimeError.
    # Create a subdirectory so --root exists but isn't a needlings repo.
    non_needlings_dir = tmp_path / "not_needlings"
    non_needlings_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(cli, ["--root", str(non_needlings_dir), "list"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_cli_list_with_malformed_catalog_shows_clean_error(tmp_path: Path) -> None:
    # exercises/ exists but contains a broken chapter that references missing exercise.
    ex = tmp_path / "exercises"
    ex.mkdir()
    (ex / "_base").mkdir()
    ch = ex / "01-setup"
    ch.mkdir()
    # index.toml references an exercise that doesn't exist
    (ch / "index.toml").write_text('title = "Setup"\nexercises = ["ex-1"]\n')

    runner = CliRunner()
    result = runner.invoke(cli, ["--root", str(tmp_path), "list"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
