"""Tests for components/xattrs/claude_code_guidelines.py.tftpl."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

from tests._helpers import XATTRS_DIR, render_template

EA_TEMPLATE = XATTRS_DIR / "claude_code_guidelines.py.tftpl"


def run_ea(target: Path, expected_hash: str, work_dir: Path) -> str:
    """Render the EA template, run it as a subprocess, return its stdout."""
    source = render_template(EA_TEMPLATE, {"expected_sha256": expected_hash})
    source = source.replace(
        'Path("/Library/Application Support/ClaudeCode/CLAUDE.md")',
        f'Path("{target}")',
    )

    test_path = work_dir / "ea_under_test.py"
    test_path.write_text(source)

    result = subprocess.run(
        [sys.executable, str(test_path)],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_returns_compliant_when_hash_matches(tmp_path):
    content = b"# Stark Industries Guidelines\n"
    target = tmp_path / "CLAUDE.md"
    target.write_bytes(content)
    expected = hashlib.sha256(content).hexdigest()

    output = run_ea(target, expected, tmp_path)

    assert output == "<result>Compliant</result>"


def test_returns_modified_when_hash_does_not_match(tmp_path):
    target = tmp_path / "CLAUDE.md"
    target.write_bytes(b"someone has tampered with this")
    wrong_hash = hashlib.sha256(b"original content").hexdigest()

    output = run_ea(target, wrong_hash, tmp_path)

    assert output == "<result>Modified</result>"


def test_returns_missing_when_target_does_not_exist(tmp_path):
    target = tmp_path / "definitely_not_there.md"
    expected = hashlib.sha256(b"anything").hexdigest()

    output = run_ea(target, expected, tmp_path)

    assert output == "<result>Missing</result>"
