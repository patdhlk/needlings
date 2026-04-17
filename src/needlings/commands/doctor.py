"""`needlings doctor` — diagnose environment problems."""
from __future__ import annotations

import shutil
import subprocess
import sys

import click


@click.command("doctor")
@click.pass_context
def doctor_command(ctx: click.Context) -> None:
    """Diagnose environment prerequisites and print a checklist."""
    checks: list[tuple[str, bool, str]] = []

    # Python version
    py_ok = sys.version_info >= (3, 11)
    checks.append((
        "python >= 3.11",
        py_ok,
        ".".join(str(p) for p in sys.version_info[:3]),
    ))

    # uv present
    uv_path = shutil.which("uv")
    checks.append(("uv on PATH", uv_path is not None, uv_path or "missing"))

    # ubc present
    ubc_path = shutil.which("ubc")
    ubc_version = _check_version("ubc", "--version") if ubc_path else "missing"
    checks.append(("ubc on PATH", ubc_path is not None, ubc_version))

    # sphinx
    sphinx_ok, sphinx_v = _import_version("sphinx")
    checks.append(("sphinx importable", sphinx_ok, sphinx_v))

    # sphinx-needs
    sn_ok, sn_v = _import_version("sphinx_needs")
    checks.append(("sphinx-needs importable", sn_ok, sn_v))

    for label, ok, detail in checks:
        mark = click.style("✓", fg="green") if ok else click.style("✗", fg="red")
        click.echo(f"{mark} {label}: {detail}")

    if not all(ok for _, ok, _ in checks):
        ctx.exit(1)


def _check_version(cmd: str, flag: str) -> str:
    try:
        out = subprocess.run(
            [cmd, flag], capture_output=True, text=True, check=True
        )
        return (out.stdout + out.stderr).strip().splitlines()[0]
    except Exception:
        return "unknown"


def _import_version(module: str) -> tuple[bool, str]:
    try:
        mod = __import__(module)
        return True, str(getattr(mod, "__version__", "unknown"))
    except ImportError:
        return False, "not installed"
