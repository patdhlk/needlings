from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from needlings.cli import cli
from tests.unit.test_catalog import _scaffold


def test_init_creates_state(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    with patch("needlings.commands.init.ensure_ubc", return_value="/usr/bin/ubc"):
        result = runner.invoke(cli, ["--root", str(tmp_path), "init"])
    assert result.exit_code == 0, result.output

    state_file = tmp_path / ".needlings" / "state.json"
    assert state_file.exists()


def test_init_is_idempotent(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    with patch("needlings.commands.init.ensure_ubc", return_value="/usr/bin/ubc"):
        runner.invoke(cli, ["--root", str(tmp_path), "init"])
        result = runner.invoke(cli, ["--root", str(tmp_path), "init"])
    assert result.exit_code == 0


def test_init_with_missing_ubc_prints_instructions_not_traceback(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    # Simulate ubc not installed by letting ensure_ubc raise
    with patch(
        "needlings.commands.init.ensure_ubc",
        side_effect=RuntimeError("ubc (the useblocks CLI) was not found on PATH."),
    ):
        result = runner.invoke(cli, ["--root", str(tmp_path), "init"])
    # Should NOT fail — init is soft on ubc absence
    assert result.exit_code == 0, result.output
    assert "Traceback" not in result.output
    assert "ubc" in result.output  # instructions echoed to stderr


def test_init_skip_ubc_check_does_not_call_ensure_ubc(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    with patch("needlings.commands.init.ensure_ubc") as mock_ensure:
        result = runner.invoke(
            cli, ["--root", str(tmp_path), "init", "--skip-ubc-check"]
        )
    assert result.exit_code == 0
    mock_ensure.assert_not_called()
    assert "skipped ubc check" in result.output
