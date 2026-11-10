"""Core regression tests for mdtoolkit."""

import sys

import pytest

from mdtoolkit import __version__
from mdtoolkit.__main__ import main


@pytest.mark.parametrize("flag", ["-h", "--help"])
def test_help_flag_prints_usage_and_exits_zero(capsys, monkeypatch, flag):
    """`-h`/`--help` must print usage and exit 0, not hit file loading."""
    monkeypatch.setattr(sys, "argv", ["mdtoolkit", flag])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "Usage:" in out
    assert "--help" in out
    assert "--version" in out


def test_version_flag_still_exits_zero(capsys, monkeypatch):
    """Guard the existing `-v`/`--version` behaviour (exit 0 + version)."""
    monkeypatch.setattr(sys, "argv", ["mdtoolkit", "--version"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out
