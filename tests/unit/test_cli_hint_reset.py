from pathlib import Path

from click.testing import CliRunner

from needlings.cli import cli
from tests.unit.test_catalog import _scaffold


def test_hint_prints_hint(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "hint", "01-setup/01-hello"]
    )
    assert result.exit_code == 0, result.output
    assert "hint 1" in result.output


def test_reset_restores_starter(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()

    starter = tmp_path / "exercises/01-setup/01-hello/starter/index.rst"
    starter.write_text("learner edits!\n")

    result = runner.invoke(
        cli, ["--root", str(tmp_path), "reset", "01-setup/01-hello", "--yes"]
    )
    assert result.exit_code == 0, result.output
    assert ".. I AM NOT DONE" in starter.read_text()
