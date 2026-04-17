"""`needlings init` — initialize state and verify prerequisites."""
from __future__ import annotations

import click

from needlings.state import State
from needlings.ubc_install import ensure_ubc


@click.command("init")
@click.option(
    "--skip-ubc-check", is_flag=True,
    help="Don't fail if ubc is missing (useful in CI before ubc is installed).",
)
@click.pass_context
def init_command(ctx: click.Context, skip_ubc_check: bool) -> None:
    """Create state file and check prerequisites."""
    paths = ctx.obj["paths"]
    try:
        paths.state_dir.mkdir(parents=True, exist_ok=True)
        state = State.load(paths.state_file)
        state.save()
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"state file at {paths.state_file}")

    if skip_ubc_check:
        click.echo("skipped ubc check")
        return
    try:
        ubc = ensure_ubc()
        click.echo(f"found ubc at {ubc}")
    except RuntimeError as e:
        click.echo(str(e), err=True)
