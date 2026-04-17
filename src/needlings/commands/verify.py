"""`needlings verify` — CI entry point."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import click

from needlings.catalog import flatten, load_catalog
from needlings.compose import compose_build_dir
from needlings.verify import VerifyOrchestrator


@click.command("verify")
@click.option("--all", "mode_all", is_flag=True,
              help="Apply each solution and expect pass.")
@click.option("--starters", "mode_starters", is_flag=True,
              help="Apply each starter and expect fail.")
@click.option("--changed", "mode_changed", is_flag=True,
              help="Verify only exercises whose files differ from the main branch.")
@click.option("--base-ref", default="main", show_default=True)
@click.option("--ubc-binary", default="ubc", show_default=True)
@click.pass_context
def verify_command(ctx: click.Context, mode_all: bool, mode_starters: bool,
                   mode_changed: bool, base_ref: str, ubc_binary: str) -> None:
    """Run verification in a CI-friendly way."""
    if sum([mode_all, mode_starters, mode_changed]) != 1:
        raise click.ClickException(
            "choose exactly one of --all, --starters, --changed"
        )

    paths = ctx.obj["paths"]
    passes = 0
    fails = 0
    try:
        orchestrator = VerifyOrchestrator.default(ubc_binary=ubc_binary)
        exercises = flatten(load_catalog(paths))

        if mode_changed:
            changed_ids = _changed_exercises(paths.root, base_ref)
            exercises = [e for e in exercises if str(e.id) in changed_ids]
            if not exercises:
                click.echo("no changed exercises")
                return

        for ex in exercises:
            overlay = Path(ex.path) / ("solution" if mode_all or mode_changed else "starter")
            with tempfile.TemporaryDirectory(prefix="needlings-verify-") as tmp:
                build_dir = Path(tmp)
                compose_build_dir(base=paths.base, starter=overlay, out=build_dir)
                results = orchestrator.run(build_dir=build_dir, exercise=ex)
                ok = orchestrator.all_passed(results)
            if mode_starters:
                ok = not ok  # starters should fail
            if ok:
                click.echo(f"✓ {ex.id}")
                passes += 1
            else:
                fails += 1
                click.echo(f"✗ {ex.id}", err=True)
                if results:
                    click.echo((results[-1].stderr or results[-1].stdout), err=True)
    except (RuntimeError, ValueError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc

    if mode_starters:
        click.echo(f"{passes} starters failed as expected, {fails} unexpectedly passed")
    else:
        click.echo(f"{passes} passed, {fails} failed")

    ctx.exit(0 if fails == 0 else 1)


def _changed_exercises(root: Path, base_ref: str) -> set[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}..HEAD"],
        cwd=root, capture_output=True, text=True,
    )
    ids: set[str] = set()
    for line in proc.stdout.splitlines():
        parts = line.split("/")
        if len(parts) >= 3 and parts[0] == "exercises":
            ids.add(f"{parts[1]}/{parts[2]}")
    return ids
