"""Shared pytest fixtures and import path setup for the test suite."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest
from tests._helpers import SCRIPTS_PYTHON_DIR, XATTRS_DIR

# Make deployment script directories importable as modules so test files can
# `import jamf_log_uploader` etc. without manual sys.path manipulation.
for _dir in (SCRIPTS_PYTHON_DIR, XATTRS_DIR):
    _path = str(_dir)
    if _path not in sys.path:
        sys.path.insert(0, _path)


@pytest.fixture(autouse=True)
def mock_pymdm(monkeypatch):
    """
    Replace ``pymdm`` with a MagicMock for every test.

    Deployment scripts import classes (MdmLogger, CommandRunner, etc.) from
    pymdm at module import time. Mocking the package keeps tests independent
    of whether pymdm is actually installed in the test environment.
    """
    pymdm_mock = MagicMock()
    monkeypatch.setitem(sys.modules, "pymdm", pymdm_mock)
    yield pymdm_mock
