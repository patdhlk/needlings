from pathlib import Path

from needlings.models import ExerciseId
from needlings.state import State


def test_state_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    s = State.load(path)
    assert s.current is None

    eid = ExerciseId("01-setup", "01-hello")
    s.mark_attempt(eid)
    s.mark_completed(eid)
    s.set_current(eid)
    s.save()

    reloaded = State.load(path)
    assert reloaded.current == eid
    assert reloaded.exercises[str(eid)].attempts == 1
    assert reloaded.exercises[str(eid)].completed_at is not None


def test_state_increments_attempts(tmp_path: Path) -> None:
    s = State.load(tmp_path / "state.json")
    eid = ExerciseId("01-setup", "01-hello")
    s.mark_attempt(eid)
    s.mark_attempt(eid)
    assert s.exercises[str(eid)].attempts == 2


def test_state_handles_missing_file(tmp_path: Path) -> None:
    s = State.load(tmp_path / "does-not-exist.json")
    assert s.current is None
    assert s.exercises == {}
