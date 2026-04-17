from unittest.mock import patch

import pytest

from needlings.ubc_install import ensure_ubc


def test_ensure_ubc_returns_path_when_found() -> None:
    with patch("needlings.ubc_install.shutil.which", return_value="/usr/bin/ubc"):
        assert ensure_ubc() == "/usr/bin/ubc"


def test_ensure_ubc_raises_when_missing() -> None:
    with patch("needlings.ubc_install.shutil.which", return_value=None), pytest.raises(
        RuntimeError, match="ubc"
    ):
        ensure_ubc()
