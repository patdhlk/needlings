"""`needlings run <id>` — one-shot verify."""
from __future__ import annotations

import tempfile
from pathlib import Path

import click
from rich.console import Console

from needlings.catalog import flatten, load_catalog
from needlings.compose import compose_build_dir
from needlings.models import ExerciseId
from needlings.render import render_failure, render_still_not_done, render_success
from needlings.sentinel import is_still_not_done
from needlings.state import State
from needlings.verify import VerifyOrchestrator


@click.command("run")
@click.argument("exercise_id")
@click.option(
    "--ubc-binary", default="ubc", show_default=True,
    help="Path / name of the ubc binary.",
)
@click.pass_context
def run_command(ctx: click.Context, exercise_id: str, ubc_binary: str) -> None:
    """Verify a single exercise once."""
    paths = ctx.obj["paths"]
    eid = ExerciseId.parse(exercise_id)
    catalog = load_catalog(paths)
    ex = next((e for e in flatten(catalog) if e.id == eid), None)
    if ex is None:
        raise click.ClickException(f"unknown exercise: {exercise_id}")

    console = Console()
    starter = Path(ex.path) / "starter"

    if is_still_not_done(starter, ex.sentinel):
        render_still_not_done(console, ex)
        return

    state = State.load(paths.state_file)
    state.mark_attempt(eid)

    orchestrator = VerifyOrchestrator.default(ubc_binary=ubc_binary)
    with tempfile.TemporaryDirectory(prefix="needlings-") as tmpdir:
        build_dir = Path(tmpdir)
        compose_build_dir(base=paths.base, starter=starter, out=build_dir)
        results = orchestrator.run(build_dir=build_dir, exercise=ex)

    if orchestrator.all_passed(results):
        state.mark_completed(eid)
        render_success(console, ex)
    else:
        render_failure(console, ex, results[-1])

    state.save()
