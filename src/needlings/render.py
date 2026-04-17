"""Rich-based rendering helpers."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from needlings.backends.base import VerifyResult
from needlings.models import Chapter, Exercise


def render_success(console: Console, exercise: Exercise) -> None:
    console.print(
        Panel.fit(
            Text(f"✓ {exercise.name} passed!", style="bold green"),
            border_style="green",
            title=str(exercise.id),
        )
    )


def render_failure(
    console: Console, exercise: Exercise, result: VerifyResult
) -> None:
    body = Text()
    body.append(f"backend: {result.backend}\n", style="yellow")
    if result.summary:
        body.append(f"{result.summary}\n\n", style="bold")
    if result.stderr:
        body.append(result.stderr.strip() + "\n", style="red")
    if result.stdout:
        body.append(result.stdout.strip() + "\n", style="dim")
    body.append("\nPress ", style="dim")
    body.append("h", style="bold cyan")
    body.append(" for a hint.", style="dim")
    console.print(
        Panel(
            body,
            border_style="red",
            title=f"✗ {exercise.name}  ({exercise.id})",
        )
    )


def render_still_not_done(console: Console, exercise: Exercise) -> None:
    console.print(
        Panel.fit(
            Text(
                f"{exercise.name}: still marked `{exercise.sentinel}`.\n"
                "Remove the sentinel when you're ready to verify.",
                style="yellow",
            ),
            border_style="yellow",
            title=str(exercise.id),
        )
    )


def render_progress_tree(
    console: Console,
    chapters: list[Chapter],
    *,
    completed: set[str],
    current_id: str | None,
) -> None:
    tree = Tree("needlings")
    for chapter in chapters:
        branch = tree.add(Text(f"{chapter.id} — {chapter.title}", style="bold"))
        for ex in chapter.exercises:
            eid = str(ex.id)
            if eid in completed:
                marker = Text("✓", style="green")
            elif eid == current_id:
                marker = Text("→", style="cyan")
            else:
                marker = Text("◯", style="dim")
            line = Text.assemble(marker, " ", ex.name, " ",
                                 Text(f"[{ex.id.slug}]", style="dim"))
            branch.add(line)
    console.print(tree)
