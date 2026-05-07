"""Tests for components/scripts/python/default_dock_docklib.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_docklib(monkeypatch):
    """
    Replace ``docklib`` with a MagicMock for every test.

    The deployment script imports ``Dock`` from docklib at module load time;
    docklib is not a guaranteed test dependency, so it gets stubbed.
    """
    docklib_mock = MagicMock()
    monkeypatch.setitem(sys.modules, "docklib", docklib_mock)
    yield docklib_mock


@pytest.fixture
def dd(mock_pymdm, mock_docklib):
    if "default_dock_docklib" in sys.modules:
        del sys.modules["default_dock_docklib"]
    import default_dock_docklib as module

    return module


def configure_user(mock_pymdm, username="test", home=None):
    if home is None:
        home = Path("/Users") / username
    mock_pymdm.SystemInfo.get_console_user.return_value = (username, 501, home)


def test_constructs_dock_with_console_user_plist_path(dd, mock_pymdm, mock_docklib, monkeypatch):
    home = Path("/Users/alerman")
    configure_user(mock_pymdm, username="alerman", home=home)
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = None

    monkeypatch.setattr(dd.Path, "exists", lambda self: True)
    monkeypatch.setattr(dd.subprocess, "run", lambda *a, **k: MagicMock(returncode=0))
    mock_docklib.Dock.return_value.findExistingLabel.return_value = -1

    dd.main()

    expected = str(home / "Library" / "Preferences" / "com.apple.dock.plist")
    mock_docklib.Dock.assert_called_once_with(filename=expected)


def test_skips_apps_not_present_on_disk(dd, mock_pymdm, mock_docklib, monkeypatch):
    configure_user(mock_pymdm)
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = None

    monkeypatch.setattr(dd.Path, "exists", lambda self: False)
    monkeypatch.setattr(dd.subprocess, "run", lambda *a, **k: MagicMock(returncode=0))

    dd.main()

    mock_docklib.Dock.return_value.makeDockAppEntry.assert_not_called()


def test_skips_apps_already_in_dock(dd, mock_pymdm, mock_docklib, monkeypatch):
    configure_user(mock_pymdm)
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = None

    monkeypatch.setattr(dd.Path, "exists", lambda self: True)
    monkeypatch.setattr(dd.subprocess, "run", lambda *a, **k: MagicMock(returncode=0))

    # findExistingLabel >= 0 means the app is already in the dock.
    mock_docklib.Dock.return_value.findExistingLabel.return_value = 0

    dd.main()

    mock_docklib.Dock.return_value.makeDockAppEntry.assert_not_called()


def test_dry_run_does_not_save(dd, mock_pymdm, mock_docklib, monkeypatch):
    configure_user(mock_pymdm)
    mock_pymdm.ParamParser.get_bool.return_value = True
    mock_pymdm.ParamParser.get.return_value = None

    monkeypatch.setattr(dd.Path, "exists", lambda self: True)
    monkeypatch.setattr(dd.subprocess, "run", lambda *a, **k: MagicMock(returncode=0))

    mock_docklib.Dock.return_value.findExistingLabel.return_value = -1

    dd.main()

    mock_docklib.Dock.return_value.save.assert_not_called()


def test_saves_and_restarts_dock_when_not_dry_run(dd, mock_pymdm, mock_docklib, monkeypatch):
    configure_user(mock_pymdm, username="alerman")
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = None

    monkeypatch.setattr(dd.Path, "exists", lambda self: True)
    runs = []
    monkeypatch.setattr(
        dd.subprocess,
        "run",
        lambda cmd, **kw: runs.append(cmd) or MagicMock(returncode=0),
    )

    mock_docklib.Dock.return_value.findExistingLabel.return_value = -1

    dd.main()

    mock_docklib.Dock.return_value.save.assert_called_once()
    killalls = [r for r in runs if r[0] == "/usr/bin/killall"]
    assert killalls
    assert "alerman" in killalls[0]
    assert "Dock" in killalls[0]


def test_extra_app_passed_to_make_dock_app_entry(dd, mock_pymdm, mock_docklib, monkeypatch):
    configure_user(mock_pymdm)
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = "/Applications/Firefox.app"

    monkeypatch.setattr(dd.Path, "exists", lambda self: True)
    monkeypatch.setattr(dd.subprocess, "run", lambda *a, **k: MagicMock(returncode=0))

    mock_docklib.Dock.return_value.findExistingLabel.return_value = -1

    dd.main()

    entry_calls = [
        c.args[0] for c in mock_docklib.Dock.return_value.makeDockAppEntry.call_args_list
    ]
    assert "/Applications/Firefox.app" in entry_calls


def test_no_console_user_skips_dock_construction(dd, mock_pymdm, mock_docklib, monkeypatch):
    mock_pymdm.SystemInfo.get_console_user.return_value = None
    mock_pymdm.ParamParser.get_bool.return_value = False
    mock_pymdm.ParamParser.get.return_value = None

    monkeypatch.setattr(dd.Path, "exists", lambda self: True)
    monkeypatch.setattr(dd.subprocess, "run", lambda *a, **k: MagicMock(returncode=0))

    dd.main()

    mock_docklib.Dock.assert_not_called()
