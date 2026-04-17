from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from needlings.backends.base import VerifyResult
from needlings.cli import cli
from tests.unit.test_catalog import _scaffold


@pytest.mark.integration
def test_verify_all_with_solutions_all_pass(tmp_path: Path) -> None:
    _scaffold(tmp_path)

    class FakeOrch:
        def run(self, *, build_dir: Path, exercise: object) -> list[VerifyResult]:
            return [VerifyResult.success("sphinx")]
        def all_passed(self, results: list[VerifyResult]) -> bool:
            return True

    runner = CliRunner()
    with patch(
        "needlings.commands.verify.VerifyOrchestrator.default",
        return_value=FakeOrch(),
    ):
        result = runner.invoke(cli, ["--root", str(tmp_path), "verify", "--all"])
    assert result.exit_code == 0, result.output
    assert "2 passed" in result.output


@pytest.mark.integration
def test_verify_starters_all_fail(tmp_path: Path) -> None:
    _scaffold(tmp_path)

    class FakeOrch:
        def run(self, *, build_dir: Path, exercise: object) -> list[VerifyResult]:
            return [VerifyResult.failure("sphinx", stderr="x")]
        def all_passed(self, results: list[VerifyResult]) -> bool:
            return False

    runner = CliRunner()
    with patch(
        "needlings.commands.verify.VerifyOrchestrator.default",
        return_value=FakeOrch(),
    ):
        result = runner.invoke(
            cli, ["--root", str(tmp_path), "verify", "--starters"]
        )
    assert result.exit_code == 0, result.output
    assert "2 starters failed as expected" in result.output


@pytest.mark.integration
def test_verify_requires_exactly_one_mode(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["--root", str(tmp_path), "verify"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert "--all" in result.output or "exactly one" in result.output


@pytest.mark.integration
def test_verify_errors_cleanly_on_malformed_catalog(tmp_path: Path) -> None:
    paths = _scaffold(tmp_path)
    # Break catalog: reference a slug that doesn't exist
    idx = paths.exercises / "01-setup" / "index.toml"
    idx.write_text('title = "Setup"\nexercises = ["01-hello", "03-missing"]\n')
    runner = CliRunner()
    result = runner.invoke(cli, ["--root", str(tmp_path), "verify", "--all"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
