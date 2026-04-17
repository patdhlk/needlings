"""`needlings progress` — summary of completed / total exercises."""
from __future__ import annotations

import click
from rich.console import Console

from needlings.catalog import flatten, load_catalog
from needlings.render import render_progress_tree
from needlings.state import State


@click.command("progress")
@click.pass_context
def progress_command(ctx: click.Context) -> None:
    """Show completed / total exercises and the full progress tree."""
    try:
        paths = ctx.obj["paths"]
        console = Console()

        catalog = load_catalog(paths)
        state = State.load(paths.state_file)
        total = len(flatten(catalog))
        completed_ids = {k for k, v in state.exercises.items() if v.completed_at}

        click.echo(f"{len(completed_ids)} / {total} exercises complete")
        render_progress_tree(
            console, catalog,
            completed=completed_ids,
            current_id=str(state.current) if state.current else None,
        )
    except (RuntimeError, ValueError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
