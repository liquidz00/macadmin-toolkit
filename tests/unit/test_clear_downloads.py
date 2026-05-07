"""Tests for components/scripts/python/clear_downloads.py."""

from __future__ import annotations

import sys

import pytest


@pytest.fixture
def cd():
    """Yield clear_downloads with a fresh import so module-level state is clean."""
    if "clear_downloads" in sys.modules:
        del sys.modules["clear_downloads"]
    import clear_downloads as module

    return module


def test_removes_files_in_downloads(cd, mock_pymdm, tmp_path):
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    (downloads / "a.txt").write_text("x")
    (downloads / "b.pdf").write_text("y")

    mock_pymdm.SystemInfo.get_console_user.return_value = ("test", 501, tmp_path)
    mock_pymdm.ParamParser.get_bool.return_value = False

    cd.main()

    assert list(downloads.iterdir()) == []


def test_removes_directories_recursively(cd, mock_pymdm, tmp_path):
    downloads = tmp_path / "Downloads"
    nested = downloads / "subdir" / "deep"
    nested.mkdir(parents=True)
    (nested / "f").write_text("x")

    mock_pymdm.SystemInfo.get_console_user.return_value = ("test", 501, tmp_path)
    mock_pymdm.ParamParser.get_bool.return_value = False

    cd.main()

    assert list(downloads.iterdir()) == []


def test_dry_run_does_not_delete(cd, mock_pymdm, tmp_path):
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    (downloads / "a.txt").write_text("x")

    mock_pymdm.SystemInfo.get_console_user.return_value = ("test", 501, tmp_path)
    mock_pymdm.ParamParser.get_bool.return_value = True

    cd.main()

    assert (downloads / "a.txt").exists()


def test_no_console_user_returns_without_action(cd, mock_pymdm, tmp_path):
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    (downloads / "a.txt").write_text("x")

    mock_pymdm.SystemInfo.get_console_user.return_value = None
    mock_pymdm.ParamParser.get_bool.return_value = False

    cd.main()

    assert (downloads / "a.txt").exists()


def test_missing_downloads_folder_does_not_raise(cd, mock_pymdm, tmp_path):
    # tmp_path itself exists, but no Downloads/ inside it.
    mock_pymdm.SystemInfo.get_console_user.return_value = ("test", 501, tmp_path)
    mock_pymdm.ParamParser.get_bool.return_value = False

    cd.main()  # should warn and return cleanly
