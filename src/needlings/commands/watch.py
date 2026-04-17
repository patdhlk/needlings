"""`needlings watch` — file-watch + verify loop."""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import click
from rich.console import Console
from watchfiles import Change, awatch

from needlings.catalog import flatten, load_catalog
from needlings.compose import compose_build_dir
from needlings.models import Exercise
from needlings.paths import Paths
from needlings.render import render_failure, render_still_not_done, render_success
from needlings.sentinel import is_still_not_done
from needlings.state import State
from needlings.verify import VerifyOrchestrator


@click.command("watch")
@click.option("--ubc-binary", default="ubc", show_default=True)
@click.option("--debounce-ms", default=200, show_default=True, type=int)
@click.pass_context
def watch_command(ctx: click.Context, ubc_binary: str, debounce_ms: int) -> None:
    """Watch current exercise files and re-verify on save."""
    paths = ctx.obj["paths"]
    try:
        asyncio.run(_watch_loop(paths, ubc_binary=ubc_binary, debounce_ms=debounce_ms))
    except (RuntimeError, ValueError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc


async def _watch_loop(paths: Paths, *, ubc_binary: str, debounce_ms: int) -> None:
    console = Console()
    orchestrator = VerifyOrchestrator.default(ubc_binary=ubc_binary)

    while True:
        catalog = load_catalog(paths)
        exercises = flatten(catalog)
        state = State.load(paths.state_file)

        current = _pick_next(exercises, state)
        if current is None:
            console.print("[green bold]All exercises complete! 🎉[/]")
            return
        state.set_current(current.id)
        state.save()

        console.rule(f"[cyan]{current.id} — {current.name}[/]")
        if await _run_once(paths, current, orchestrator, console, state):
            continue  # advance loop

        await _await_change_with_debounce(
            Path(current.path) / "starter", debounce_ms=debounce_ms,
        )


def _pick_next(exercises: list[Exercise], state: State) -> Exercise | None:
    # Resume at stored current if it's still incomplete; otherwise first incomplete.
    if state.current is not None:
        for ex in exercises:
            if ex.id == state.current and not state.is_completed(ex.id):
                return ex
    for ex in exercises:
        if not state.is_completed(ex.id):
            return ex
    return None


async def _run_once(paths: Paths, ex: Exercise, orch: VerifyOrchestrator,
                    console: Console, state: State) -> bool:
    """Run verify; return True on success (advance), False on fail (stay)."""
    starter = Path(ex.path) / "starter"

    if is_still_not_done(starter, ex.sentinel):
        render_still_not_done(console, ex)
        return False

    state.mark_attempt(ex.id)
    with tempfile.TemporaryDirectory(prefix="needlings-") as tmp:
        build_dir = Path(tmp)
        compose_build_dir(base=paths.base, starter=starter, out=build_dir)
        results = orch.run(build_dir=build_dir, exercise=ex)

    if orch.all_passed(results):
        state.mark_completed(ex.id)
        state.save()
        render_success(console, ex)
        return True
    if results:
        render_failure(console, ex, results[-1])
    else:
        console.print(f"[red]no backends configured for {ex.id}[/]")
    state.save()
    return False


async def _await_change_with_debounce(path: Path, *, debounce_ms: int) -> None:
    async for changes in awatch(path, step=debounce_ms):
        if any(c[0] in (Change.added, Change.modified) for c in changes):
            return
