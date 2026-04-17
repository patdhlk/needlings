"""`needlings list` — print the progress tree."""
from __future__ import annotations

import click
from rich.console import Console

from needlings.catalog import load_catalog
from needlings.render import render_progress_tree
from needlings.state import State


@click.command("list")
@click.pass_context
def list_command(ctx: click.Context) -> None:
    """List all chapters and exercises with progress markers."""
    paths = ctx.obj["paths"]
    console = Console()
    catalog = load_catalog(paths)
    state = State.load(paths.state_file)
    completed = {k for k, v in state.exercises.items() if v.completed_at}
    render_progress_tree(
        console, catalog,
        completed=completed,
        current_id=str(state.current) if state.current else None,
    )
