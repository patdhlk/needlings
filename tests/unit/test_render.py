from io import StringIO

from rich.console import Console

from needlings.backends.base import VerifyResult
from needlings.models import Chapter, Exercise, ExerciseId, VerifyConfig
from needlings.render import render_failure, render_progress_tree, render_success


def _console() -> Console:
    return Console(file=StringIO(), width=80, record=True, force_terminal=False)


def _ex(chapter: str, slug: str, name: str) -> Exercise:
    return Exercise(
        id=ExerciseId(chapter, slug), name=name, order=1, hint="h",
        sentinel=".. I AM NOT DONE", verify=VerifyConfig(backend=["sphinx"]),
    )


def test_render_success_shows_name() -> None:
    c = _console()
    render_success(c, _ex("01", "01-x", "Hello"))
    out = c.export_text()
    assert "Hello" in out
    assert "✓" in out or "passed" in out.lower()


def test_render_failure_shows_backend_and_stderr() -> None:
    c = _console()
    result = VerifyResult.failure("sphinx", stderr="boom line", summary="sb")
    render_failure(c, _ex("01", "01-x", "Hello"), result)
    out = c.export_text()
    assert "sphinx" in out
    assert "boom line" in out


def test_render_progress_tree_shows_chapters() -> None:
    c = _console()
    chapter = Chapter(id="01-setup", title="Setup",
                      exercises=[_ex("01-setup", "01-hello", "Hello")])
    render_progress_tree(c, [chapter], completed={"01-setup/01-hello"},
                         current_id="01-setup/01-hello")
    out = c.export_text()
    assert "Setup" in out
    assert "Hello" in out


def test_render_failure_shows_summary_when_set() -> None:
    c = _console()
    result = VerifyResult.failure("sphinx", summary="build exited 1")
    render_failure(c, _ex("01", "01-x", "Hello"), result)
    out = c.export_text()
    assert "build exited 1" in out


def test_render_failure_shows_stdout_when_set() -> None:
    c = _console()
    result = VerifyResult.failure("sphinx", stdout="warning: foo")
    render_failure(c, _ex("01", "01-x", "Hello"), result)
    out = c.export_text()
    assert "warning: foo" in out


def test_render_progress_tree_marks_current_exercise() -> None:
    c = _console()
    chapter = Chapter(id="01-setup", title="Setup",
                      exercises=[_ex("01-setup", "01-hello", "Hello")])
    render_progress_tree(c, [chapter], completed=set(),
                         current_id="01-setup/01-hello")
    out = c.export_text()
    assert "→" in out


def test_render_progress_tree_marks_pending_exercise() -> None:
    c = _console()
    chapter = Chapter(id="01-setup", title="Setup",
                      exercises=[_ex("01-setup", "01-hello", "Hello")])
    render_progress_tree(c, [chapter], completed=set(), current_id=None)
    out = c.export_text()
    assert "◯" in out
