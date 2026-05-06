"""
Shared utilities for the test suite.

Mostly concerned with loading the .py.tftpl deployment scripts in a way the
test runner can exercise — substitute ${...} placeholders, write the rendered
source to a temp file, and import it as a Python module.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).parent.parent
SCRIPTS_PYTHON_DIR = REPO_ROOT / "components" / "scripts" / "python"
XATTRS_DIR = REPO_ROOT / "components" / "xattrs"


def render_template(template_path: Path, substitutions: dict[str, str]) -> str:
    """
    Render a .py.tftpl by performing literal ``${key}`` substitutions.

    :param template_path: Path to the .py.tftpl source
    :type template_path: Path
    :param substitutions: Mapping of placeholder name to replacement value
    :type substitutions: dict[str, str]
    :return: Rendered Python source
    :rtype: str
    """
    rendered = template_path.read_text()
    for key, value in substitutions.items():
        rendered = rendered.replace(f"${{{key}}}", value)
    return rendered


def load_module_from_source(name: str, source: str, path: Path) -> ModuleType:
    """
    Write ``source`` to ``path`` and load it as a Python module.

    :param name: Module name to register under ``sys.modules``
    :type name: str
    :param source: Python source code
    :type source: str
    :param path: Filesystem path to write the source to
    :type path: Path
    :return: Loaded module
    :rtype: ModuleType
    """
    path.write_text(source)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
