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


def test_hint_with_malformed_id_shows_clean_error(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "hint", "nope"]
    )
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_hint_with_unknown_id_shows_clean_error(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "hint", "99-fake/99-fake"]
    )
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_reset_with_malformed_id_shows_clean_error(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "reset", "nope", "--yes"]
    )
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_reset_with_unknown_id_shows_clean_error(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "reset", "99-fake/99-fake", "--yes"]
    )
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_reset_with_missing_pristine_shows_clean_error(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    # Remove the .pristine directory to trigger the error
    pristine_path = tmp_path / "exercises/01-setup/01-hello/starter/.pristine"
    if pristine_path.exists():
        import shutil
        shutil.rmtree(pristine_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "reset", "01-setup/01-hello", "--yes"]
    )
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_reset_declined_exits_nonzero(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "reset", "01-setup/01-hello"],
        input="n\n"
    )
    assert result.exit_code != 0
    assert "Traceback" not in result.output
