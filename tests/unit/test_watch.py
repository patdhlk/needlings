import asyncio
import time
from pathlib import Path
from unittest.mock import MagicMock

from click.testing import CliRunner

from needlings.cli import cli
from needlings.watch import debounce


def test_debounce_coalesces_events() -> None:
    calls: list[int] = []

    async def scenario() -> None:
        fn = MagicMock(side_effect=lambda: calls.append(time.monotonic()))
        trigger = debounce(fn, delay_ms=100)
        trigger()
        trigger()
        await asyncio.sleep(0.05)
        trigger()
        await asyncio.sleep(0.2)
        assert fn.call_count == 1

    asyncio.run(scenario())


def test_debounce_fires_again_after_delay() -> None:
    async def scenario() -> None:
        fn = MagicMock()
        trigger = debounce(fn, delay_ms=50)
        trigger()
        await asyncio.sleep(0.15)
        trigger()
        await asyncio.sleep(0.15)
        assert fn.call_count == 2

    asyncio.run(scenario())


def test_watch_with_empty_root_shows_clean_error(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    runner = CliRunner()
    result = runner.invoke(cli, ["--root", str(empty), "watch"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
