from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from needlings.backends.base import VerifyResult
from needlings.cli import cli
from tests.unit.test_catalog import _scaffold


def test_run_success_updates_state(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    # Remove sentinel so verify proceeds
    starter = tmp_path / "exercises/01-setup/01-hello/starter/index.rst"
    starter.write_text(".. req:: hi\n   :id: REQ_HI\n")
    pristine = tmp_path / "exercises/01-setup/01-hello/starter/.pristine/index.rst"
    pristine.write_text(".. req:: hi\n   :id: REQ_HI\n")

    fake = MagicMock()
    fake.run.return_value = [VerifyResult.success("sphinx")]
    fake.all_passed.return_value = True

    runner = CliRunner()
    with patch(
        "needlings.commands.run.VerifyOrchestrator.default", return_value=fake
    ):
        result = runner.invoke(
            cli, ["--root", str(tmp_path), "run", "01-setup/01-hello"]
        )
    assert result.exit_code == 0, result.output
    assert "passed" in result.output.lower() or "✓" in result.output

    from needlings.state import State
    state = State.load(tmp_path / ".needlings" / "state.json")
    assert state.is_completed(
        __import__("needlings.models", fromlist=["ExerciseId"])
        .ExerciseId("01-setup", "01-hello")
    )


def test_run_still_not_done(tmp_path: Path) -> None:
    _scaffold(tmp_path)  # starter still has sentinel

    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "run", "01-setup/01-hello"]
    )
    assert result.exit_code == 0
    assert "not done" in result.output.lower()
