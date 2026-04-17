"""`needlings reset <id>` — restore starter files from `.pristine/`."""
from __future__ import annotations

import shutil
from pathlib import Path

import click

from needlings.catalog import flatten, load_catalog
from needlings.models import ExerciseId


@click.command("reset")
@click.argument("exercise_id")
@click.option("--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def reset_command(ctx: click.Context, exercise_id: str, yes: bool) -> None:
    """Reset an exercise's starter files to their pristine state."""
    paths = ctx.obj["paths"]
    eid = ExerciseId.parse(exercise_id)
    catalog = load_catalog(paths)
    match = next((e for e in flatten(catalog) if e.id == eid), None)
    if match is None:
        raise click.ClickException(f"unknown exercise: {exercise_id}")

    starter = Path(match.path) / "starter"
    pristine = starter / ".pristine"
    if not pristine.exists():
        raise click.ClickException(
            f"no pristine snapshot at {pristine}; exercise cannot be reset."
        )

    if not yes and not click.confirm(
        f"This will overwrite your edits in {starter}. Continue?", default=False
    ):
        return

    for item in starter.iterdir():
        if item.name == ".pristine":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    for item in pristine.rglob("*"):
        rel = item.relative_to(pristine)
        target = starter / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)

    click.echo(f"reset {eid}")
