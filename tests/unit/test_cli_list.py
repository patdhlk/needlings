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
