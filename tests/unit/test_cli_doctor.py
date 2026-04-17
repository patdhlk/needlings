from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from needlings.cli import cli
from tests.unit.test_catalog import _scaffold


def test_doctor_reports_checks(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    with patch("needlings.commands.doctor.shutil.which", side_effect=lambda x: "/x"), \
         patch("needlings.commands.doctor._check_version", return_value="1.2.3"):
        result = runner.invoke(cli, ["--root", str(tmp_path), "doctor"])
    assert result.exit_code == 0, result.output
    assert "python" in result.output.lower()
    assert "sphinx-needs" in result.output.lower()
    assert "ubc" in result.output.lower()


def test_doctor_with_all_missing_exits_nonzero_cleanly(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    # Simulate all tools missing: shutil.which returns None
    with patch("needlings.commands.doctor.shutil.which", return_value=None), \
         patch("needlings.commands.doctor._import_version", return_value=(False, "not installed")):
        result = runner.invoke(cli, ["--root", str(tmp_path), "doctor"])
    assert result.exit_code == 1
    assert "Traceback" not in result.output
    # All checks should fail visibly
    assert "missing" in result.output.lower() or "not installed" in result.output.lower()
