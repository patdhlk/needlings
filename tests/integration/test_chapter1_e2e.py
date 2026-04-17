"""End-to-end: apply every chapter 1 solution, verify with real sphinx-build."""
from pathlib import Path

import pytest
from click.testing import CliRunner

from needlings.cli import cli

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_all_chapter1_solutions_pass() -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(REPO_ROOT), "verify", "--all"],
    )
    assert result.exit_code == 0, result.output


@pytest.mark.integration
def test_all_chapter1_starters_fail_as_expected() -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(REPO_ROOT), "verify", "--starters"],
    )
    assert result.exit_code == 0, result.output
