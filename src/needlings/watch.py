"""Debounced async helper for file watching."""
from __future__ import annotations

import asyncio
from collections.abc import Callable


def debounce(fn: Callable[[], None], *, delay_ms: int) -> Callable[[], None]:
    """Return a callable that invokes `fn` at most once per debounced window."""
    task_ref: dict[str, asyncio.Task[None] | None] = {"t": None}

    async def _delayed() -> None:
        await asyncio.sleep(delay_ms / 1000)
        fn()

    def trigger() -> None:
        existing = task_ref["t"]
        if existing and not existing.done():
            existing.cancel()
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        task_ref["t"] = loop.create_task(_delayed())

    return trigger
