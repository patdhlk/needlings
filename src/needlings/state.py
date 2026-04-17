"""Persist per-learner progress to `.needlings/state.json`."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from needlings.models import ExerciseId, ExerciseState

SCHEMA_VERSION = 1


@dataclass
class State:
    path: Path
    schema_version: int = SCHEMA_VERSION
    current: ExerciseId | None = None
    started_at: str | None = None
    exercises: dict[str, ExerciseState] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> State:
        if not path.exists():
            return cls(path=path, started_at=_now())
        raw = json.loads(path.read_text(encoding="utf-8"))
        current = raw.get("current_exercise")
        exercises = {
            k: ExerciseState(
                completed_at=v.get("completed_at"),
                attempts=int(v.get("attempts", 0)),
                hint_viewed=bool(v.get("hint_viewed", False)),
            )
            for k, v in raw.get("exercises", {}).items()
        }
        return cls(
            path=path,
            schema_version=int(raw.get("schema_version", SCHEMA_VERSION)),
            current=ExerciseId.parse(current) if current else None,
            started_at=raw.get("started_at"),
            exercises=exercises,
        )

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "schema_version": self.schema_version,
                    "current_exercise": str(self.current) if self.current else None,
                    "started_at": self.started_at,
                    "exercises": {
                        k: {
                            "completed_at": v.completed_at,
                            "attempts": v.attempts,
                            "hint_viewed": v.hint_viewed,
                        }
                        for k, v in self.exercises.items()
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def mark_attempt(self, eid: ExerciseId) -> None:
        entry = self.exercises.setdefault(str(eid), ExerciseState())
        entry.attempts += 1

    def mark_completed(self, eid: ExerciseId) -> None:
        entry = self.exercises.setdefault(str(eid), ExerciseState())
        entry.completed_at = _now()

    def mark_hint_viewed(self, eid: ExerciseId) -> None:
        entry = self.exercises.setdefault(str(eid), ExerciseState())
        entry.hint_viewed = True

    def set_current(self, eid: ExerciseId | None) -> None:
        self.current = eid

    def is_completed(self, eid: ExerciseId) -> bool:
        entry = self.exercises.get(str(eid))
        return entry is not None and entry.completed_at is not None


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")
