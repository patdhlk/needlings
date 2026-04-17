"""Top-level Click CLI for needlings."""
from __future__ import annotations

from pathlib import Path

import click

from needlings import __version__
from needlings.commands.list_ import list_command
from needlings.paths import Paths


@click.group()
@click.option(
    "--root", type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Path to the needlings repository root. Defaults to autodetect.",
)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx: click.Context, root: Path | None) -> None:
    """needlings — interactive sphinx-needs exercises."""
    ctx.ensure_object(dict)
    ctx.obj["paths"] = Paths.from_root(root) if root else Paths.discover()


cli.add_command(list_command)
