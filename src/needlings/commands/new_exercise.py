"""`needlings new-exercise` — scaffold a new exercise."""
from __future__ import annotations

import tomllib

import click

INFO_TEMPLATE = """\
name = "{name}"
chapter = "{chapter}"
order = {order}
hint = "TODO: write a short hint here."
sentinel = ".. I AM NOT DONE"

[verify]
backend = "sphinx"
flags = ["-W"]
"""

STARTER_TEMPLATE = """\
.. I AM NOT DONE

.. todo::

   TODO: the learner fills this in.
"""

SOLUTION_TEMPLATE = """\
.. req:: Example
   :id: REQ_EXAMPLE

   A solved example.
"""


@click.command("new-exercise")
@click.argument("exercise_id")  # e.g. "01-setup/03-new"
@click.option("--name", required=True)
@click.pass_context
def new_exercise_command(ctx: click.Context, exercise_id: str, name: str) -> None:
    """Scaffold a new exercise and append it to the chapter index."""
    paths = ctx.obj["paths"]
    parts = exercise_id.split("/", maxsplit=1)
    if len(parts) != 2:
        raise click.ClickException("exercise id must be 'chapter/slug'")
    chapter, slug = parts

    ch_dir = paths.exercises / chapter
    if not ch_dir.is_dir():
        raise click.ClickException(f"chapter directory {ch_dir} does not exist")

    ex_dir = ch_dir / slug
    if ex_dir.exists():
        raise click.ClickException(f"{ex_dir} already exists")

    order = 0
    try:
        ex_dir.mkdir()
        (ex_dir / "starter").mkdir()
        (ex_dir / "starter" / ".pristine").mkdir()
        (ex_dir / "solution").mkdir()

        (ex_dir / "starter" / "index.rst").write_text(STARTER_TEMPLATE)
        (ex_dir / "starter" / ".pristine" / "index.rst").write_text(STARTER_TEMPLATE)
        (ex_dir / "solution" / "index.rst").write_text(SOLUTION_TEMPLATE)

        # Append to index.toml
        idx_file = ch_dir / "index.toml"
        data = tomllib.loads(idx_file.read_text())
        order = len(data.get("exercises", [])) + 1
        (ex_dir / "info.toml").write_text(
            INFO_TEMPLATE.format(name=name, chapter=chapter, order=order)
        )

        existing = data.get("exercises", [])
        existing.append(slug)
        title = data.get("title", chapter)
        lines = [f'title = "{title}"', "exercises = ["]
        lines.extend(f'    "{s}",' for s in existing)
        lines.append("]")
        idx_file.write_text("\n".join(lines) + "\n")
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"scaffolded {exercise_id} (order={order})")
