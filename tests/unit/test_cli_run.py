from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from needlings.backends.base import VerifyResult
from needlings.cli import cli
from needlings.models import ExerciseId
from needlings.state import State
from tests.unit.test_catalog import _scaffold


def test_run_success_updates_state(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    # Remove sentinel so verify proceeds (from all files under starter/)
    starter = tmp_path / "exercises/01-setup/01-hello/starter"
    (starter / "index.rst").write_text(".. req:: hi\n   :id: REQ_HI\n")
    (starter / ".pristine" / "index.rst").write_text(".. req:: hi\n   :id: REQ_HI\n")

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

    state = State.load(tmp_path / ".needlings" / "state.json")
    assert state.is_completed(ExerciseId("01-setup", "01-hello"))


def test_run_still_not_done(tmp_path: Path) -> None:
    _scaffold(tmp_path)  # starter still has sentinel

    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "run", "01-setup/01-hello"]
    )
    assert result.exit_code == 0
    assert "not done" in result.output.lower()


def test_run_with_malformed_id_shows_clean_error(tmp_path: Path) -> None:
    _scaffold(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["--root", str(tmp_path), "run", "nope"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_run_with_unknown_id_shows_clean_error(tmp_path: Path) -> None:
    _scaffold(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["--root", str(tmp_path), "run", "99-fake/99-fake"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_run_failure_does_not_mark_completed(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    # Remove sentinel so verify proceeds (from all files under starter/)
    starter = tmp_path / "exercises/01-setup/01-hello/starter"
    (starter / "index.rst").write_text(".. req:: hi\n   :id: REQ_HI\n")
    (starter / ".pristine" / "index.rst").write_text(".. req:: hi\n   :id: REQ_HI\n")

    fake = MagicMock()
    fake.run.return_value = [VerifyResult.failure("sphinx", summary="boom")]
    fake.all_passed.return_value = False

    runner = CliRunner()
    with patch(
        "needlings.commands.run.VerifyOrchestrator.default", return_value=fake
    ):
        result = runner.invoke(
            cli, ["--root", str(tmp_path), "run", "01-setup/01-hello"]
        )
    assert result.exit_code == 0

    state = State.load(tmp_path / ".needlings" / "state.json")
    eid = ExerciseId("01-setup", "01-hello")
    assert not state.is_completed(eid)
    assert state.exercises.get(str(eid)).attempts == 1
