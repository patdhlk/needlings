from pathlib import Path

from click.testing import CliRunner

from needlings.cli import cli
from tests.unit.test_catalog import _scaffold


def test_new_exercise_creates_files(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "new-exercise",
              "01-setup/03-new", "--name", "New one"]
    )
    assert result.exit_code == 0, result.output

    ex = tmp_path / "exercises" / "01-setup" / "03-new"
    assert (ex / "info.toml").exists()
    assert (ex / "starter" / "index.rst").exists()
    assert (ex / "starter" / ".pristine" / "index.rst").exists()
    assert (ex / "solution" / "index.rst").exists()

    idx_text = (tmp_path / "exercises" / "01-setup" / "index.toml").read_text()
    assert "03-new" in idx_text


def test_new_exercise_rejects_malformed_id(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "new-exercise", "noslash", "--name", "X"]
    )
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_new_exercise_rejects_existing_directory(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "new-exercise",
              "01-setup/01-hello", "--name", "Dup"]
    )
    assert result.exit_code != 0
    assert "already exists" in result.output
    assert "Traceback" not in result.output


def test_new_exercise_rejects_missing_chapter(tmp_path: Path) -> None:
    _scaffold(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["--root", str(tmp_path), "new-exercise",
              "99-does-not-exist/01-hello", "--name", "X"]
    )
    assert result.exit_code != 0
    assert "does not exist" in result.output
    assert "Traceback" not in result.output
