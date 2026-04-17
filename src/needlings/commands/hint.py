"""`needlings hint <id>` — print the stored hint."""
from __future__ import annotations

import click

from needlings.catalog import flatten, load_catalog
from needlings.models import ExerciseId
from needlings.state import State


@click.command("hint")
@click.argument("exercise_id")
@click.pass_context
def hint_command(ctx: click.Context, exercise_id: str) -> None:
    """Print the hint for an exercise."""
    paths = ctx.obj["paths"]
    eid = ExerciseId.parse(exercise_id)
    catalog = load_catalog(paths)
    match = next(
        (e for e in flatten(catalog) if e.id == eid), None
    )
    if match is None:
        raise click.ClickException(f"unknown exercise: {exercise_id}")
    click.echo(match.hint)

    state = State.load(paths.state_file)
    state.mark_hint_viewed(eid)
    state.save()
