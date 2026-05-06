"""Tests for components/scripts/python/claude_code_guidelines.py.tftpl."""

from __future__ import annotations

import base64
from pathlib import Path

import pytest
from tests._helpers import SCRIPTS_PYTHON_DIR, load_module_from_source, render_template

DEPLOY_TEMPLATE = SCRIPTS_PYTHON_DIR / "claude_code_guidelines.py.tftpl"


def render_deploy(b64_content: str, target: Path, work_dir: Path):
    """Render the deploy script with a custom TARGET, then load it as a module."""
    source = render_template(DEPLOY_TEMPLATE, {"claude_md_b64": b64_content})
    source = source.replace(
        'Path("/Library/Application Support/ClaudeCode/CLAUDE.md")',
        f'Path("{target}")',
    )
    return load_module_from_source(
        f"deploy_under_test_{target.name}",
        source,
        work_dir / "deploy_under_test.py",
    )


def test_deploy_decodes_and_writes_content(tmp_path):
    expected = b"# Test guidelines\n\nHello world.\n"
    target = tmp_path / "CLAUDE.md"

    module = render_deploy(base64.b64encode(expected).decode(), target, tmp_path)
    module.main()

    assert target.read_bytes() == expected


def test_deploy_creates_missing_parent_directories(tmp_path):
    target = tmp_path / "deeply" / "nested" / "CLAUDE.md"

    module = render_deploy(base64.b64encode(b"x").decode(), target, tmp_path)
    module.main()

    assert target.exists()
    assert target.parent.is_dir()


def test_deploy_does_not_corrupt_existing_file_on_decode_failure(tmp_path):
    target = tmp_path / "CLAUDE.md"
    target.write_bytes(b"original content")

    module = render_deploy("!!!not!valid!base64!!!", target, tmp_path)

    with pytest.raises(Exception):
        module.main()

    assert target.read_bytes() == b"original content"


def test_deploy_sets_644_permissions(tmp_path):
    target = tmp_path / "CLAUDE.md"

    module = render_deploy(base64.b64encode(b"x").decode(), target, tmp_path)
    module.main()

    assert (target.stat().st_mode & 0o777) == 0o644
