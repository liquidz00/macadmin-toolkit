"""Tests for components/scripts/python/default_dock.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def dd():
    if "default_dock" in sys.modules:
        del sys.modules["default_dock"]
    import default_dock as module

    return module


def configure_user(mock_pymdm, username="test"):
    mock_pymdm.SystemInfo.get_console_user.return_value = (
        username,
        501,
        Path("/Users") / username,
    )


def patch_subprocess_capturing(dd, monkeypatch):
    """Replace dd.subprocess.run with a no-op that records its calls."""
    runs = []
    monkeypatch.setattr(
        dd.subprocess,
        "run",
        lambda cmd, **kw: runs.append(cmd) or MagicMock(returncode=0, stderr=""),
    )
    return runs


def test_calls_dockutil_for_each_default_app(dd, mock_pymdm, monkeypatch):
    configure_user(mock_pymdm)
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = None

    monkeypatch.setattr(dd.Path, "exists", lambda self: True)
    runs = patch_subprocess_capturing(dd, monkeypatch)

    dd.main()

    add_calls = [r for r in runs if r[0] == dd.DOCKUTIL]
    assert len(add_calls) == len(dd.DEFAULT_APPS)
    for app in dd.DEFAULT_APPS:
        assert any(app in cmd for cmd in add_calls)


def test_skips_apps_that_do_not_exist(dd, mock_pymdm, monkeypatch):
    configure_user(mock_pymdm)
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = None

    # dockutil exists, but no app on disk does.
    monkeypatch.setattr(
        dd.Path,
        "exists",
        lambda self: str(self) == dd.DOCKUTIL,
    )
    runs = patch_subprocess_capturing(dd, monkeypatch)

    dd.main()

    add_calls = [r for r in runs if r[0] == dd.DOCKUTIL]
    assert add_calls == []


def test_dry_run_does_not_invoke_dockutil_or_killall(dd, mock_pymdm, monkeypatch):
    configure_user(mock_pymdm)
    mock_pymdm.ParamParser.get_bool.return_value = True
    mock_pymdm.ParamParser.get.return_value = None

    monkeypatch.setattr(dd.Path, "exists", lambda self: True)
    runs = patch_subprocess_capturing(dd, monkeypatch)

    dd.main()

    assert runs == []


def test_extra_app_appended_to_defaults(dd, mock_pymdm, monkeypatch):
    configure_user(mock_pymdm)
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = "/Applications/Firefox.app"

    monkeypatch.setattr(dd.Path, "exists", lambda self: True)
    runs = patch_subprocess_capturing(dd, monkeypatch)

    dd.main()

    add_calls = [r for r in runs if r[0] == dd.DOCKUTIL]
    assert any("/Applications/Firefox.app" in cmd for cmd in add_calls)


def test_restarts_dock_for_console_user(dd, mock_pymdm, monkeypatch):
    configure_user(mock_pymdm, username="alerman")
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = None

    monkeypatch.setattr(dd.Path, "exists", lambda self: True)
    runs = patch_subprocess_capturing(dd, monkeypatch)

    dd.main()

    killalls = [r for r in runs if r[0] == "/usr/bin/killall"]
    assert killalls
    assert "alerman" in killalls[0]
    assert "Dock" in killalls[0]


def test_no_console_user_returns_without_calling_dockutil(dd, mock_pymdm, monkeypatch):
    mock_pymdm.SystemInfo.get_console_user.return_value = None
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = None

    monkeypatch.setattr(dd.Path, "exists", lambda self: True)
    runs = patch_subprocess_capturing(dd, monkeypatch)

    dd.main()

    assert runs == []


def test_missing_dockutil_aborts_via_logger_error(dd, mock_pymdm, monkeypatch):
    configure_user(mock_pymdm)
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = None

    # Nothing exists on disk — including dockutil.
    monkeypatch.setattr(dd.Path, "exists", lambda self: False)
    runs = patch_subprocess_capturing(dd, monkeypatch)

    dd.main()

    assert runs == []
    dd.logger.error.assert_called_once()
