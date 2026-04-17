"""Repository and state-file path resolution."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    root: Path

    @property
    def exercises(self) -> Path:
        return self.root / "exercises"

    @property
    def base(self) -> Path:
        return self.exercises / "_base"

    @property
    def state_dir(self) -> Path:
        return self.root / ".needlings"

    @property
    def state_file(self) -> Path:
        return self.state_dir / "state.json"

    @property
    def crash_dir(self) -> Path:
        return self.state_dir / "crashes"

    @classmethod
    def from_root(cls, root: Path) -> Paths:
        return cls(root=root.resolve())

    @classmethod
    def discover(cls, start: Path | None = None) -> Paths:
        """Walk upward from `start` (or cwd) looking for an `exercises/` directory."""
        current = (start or Path.cwd()).resolve()
        for candidate in [current, *current.parents]:
            if (candidate / "exercises").is_dir():
                return cls.from_root(candidate)
        raise RuntimeError(
            f"Current directory ({current}) is not inside a needlings repository "
            f"(no `exercises/` directory found in any parent)."
        )
