"""Tests for components/scripts/python/jamf_log_uploader.py."""

from __future__ import annotations

import sys
from datetime import datetime
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def jlu():
    """Yield jamf_log_uploader with module-level RESULTS cleared."""
    if "jamf_log_uploader" in sys.modules:
        del sys.modules["jamf_log_uploader"]
    import jamf_log_uploader as module

    module.RESULTS.clear()
    return module


class TestSafeCopy:
    def test_copies_existing_file_and_records_ok(self, jlu, tmp_path):
        src = tmp_path / "source.txt"
        src.write_text("hello")
        dest = tmp_path / "dest"
        dest.mkdir()

        jlu._safe_copy(src, dest, step="Test")

        assert (dest / "source.txt").read_text() == "hello"
        assert jlu.RESULTS["Test"][0]["status"] == "ok"

    def test_records_warn_when_source_missing(self, jlu, tmp_path):
        dest = tmp_path / "dest"
        dest.mkdir()

        jlu._safe_copy(tmp_path / "missing.txt", dest, step="Test")

        assert jlu.RESULTS["Test"][0]["status"] == "warn"
        assert "not found" in jlu.RESULTS["Test"][0]["message"]

    def test_records_fail_on_oserror(self, jlu, tmp_path, monkeypatch):
        src = tmp_path / "source.txt"
        src.write_text("hello")
        dest = tmp_path / "dest"
        dest.mkdir()

        def boom(*args, **kwargs):
            raise OSError("permission denied")

        monkeypatch.setattr(jlu.shutil, "copy2", boom)

        jlu._safe_copy(src, dest, step="Test")

        assert jlu.RESULTS["Test"][0]["status"] == "fail"
        assert "permission denied" in jlu.RESULTS["Test"][0]["message"]


class TestSaveCommandOutput:
    def test_zero_exit_writes_stdout_and_records_ok(self, jlu, tmp_path):
        runner = MagicMock()
        runner.run.return_value = MagicMock(returncode=0, stdout="result", stderr="")

        dest = tmp_path / "out.txt"
        jlu._save_command_output(runner, ["fake"], dest, step="Test")

        assert dest.read_text() == "result"
        assert jlu.RESULTS["Test"][0]["status"] == "ok"

    def test_nonzero_exit_records_warn_and_appends_stderr(self, jlu, tmp_path):
        runner = MagicMock()
        runner.run.return_value = MagicMock(returncode=2, stdout="x", stderr="oops")

        dest = tmp_path / "out.txt"
        jlu._save_command_output(runner, ["fake"], dest, step="Test")

        assert jlu.RESULTS["Test"][0]["status"] == "warn"
        assert "exit code 2" in jlu.RESULTS["Test"][0]["message"]
        assert "oops" in dest.read_text()

    def test_runner_exception_records_fail(self, jlu, tmp_path):
        runner = MagicMock()
        runner.run.side_effect = RuntimeError("boom")

        dest = tmp_path / "out.txt"
        jlu._save_command_output(runner, ["fake"], dest, step="Test")

        assert jlu.RESULTS["Test"][0]["status"] == "fail"
        assert "boom" in jlu.RESULTS["Test"][0]["message"]
        assert not dest.exists()


class TestSendOrSave:
    def test_dry_run_skips_webhook_and_saves_locally(self, jlu, tmp_path, monkeypatch):
        archive = tmp_path / "logs.zip"
        archive.write_bytes(b"x" * 100)
        monkeypatch.setattr(jlu, "FALLBACK_OUTPUT_DIR", tmp_path / "shared")

        result = jlu._send_or_save(archive, "https://example.com/wh", {}, dry_run=True)

        assert result == tmp_path / "shared" / "logs.zip"
        assert result.exists()

    def test_no_url_saves_locally(self, jlu, tmp_path, monkeypatch):
        archive = tmp_path / "logs.zip"
        archive.write_bytes(b"x" * 100)
        monkeypatch.setattr(jlu, "FALLBACK_OUTPUT_DIR", tmp_path / "shared")

        result = jlu._send_or_save(archive, None, {}, dry_run=False)

        assert result == tmp_path / "shared" / "logs.zip"

    def test_oversized_archive_falls_back_locally(self, jlu, tmp_path, monkeypatch):
        archive = tmp_path / "logs.zip"
        archive.write_bytes(b"x" * 100)
        monkeypatch.setattr(jlu, "WEBHOOK_MAX_BYTES", 50)
        monkeypatch.setattr(jlu, "FALLBACK_OUTPUT_DIR", tmp_path / "shared")

        result = jlu._send_or_save(archive, "https://example.com/wh", {}, dry_run=False)

        assert result == tmp_path / "shared" / "logs.zip"


class TestRenderResultsHtml:
    def test_includes_one_h2_per_step(self, jlu, tmp_path):
        jlu.RESULTS.update(
            {
                "Jamf": [{"target": "/var/log/jamf.log", "status": "ok", "message": ""}],
                "SSO": [{"target": "/usr/bin/app-sso list", "status": "warn", "message": "exit 1"}],
            }
        )

        jlu._render_results_html(tmp_path, "test-mac", datetime(2026, 5, 6, 12, 0, 0))

        content = (tmp_path / "Results.html").read_text()
        assert "<h2>Jamf</h2>" in content
        assert "<h2>SSO</h2>" in content
        assert "test-mac" in content

    def test_summary_counts_match_status_distribution(self, jlu, tmp_path):
        jlu.RESULTS.update(
            {
                "Jamf": [
                    {"target": "a", "status": "ok", "message": ""},
                    {"target": "b", "status": "warn", "message": "x"},
                    {"target": "c", "status": "fail", "message": "y"},
                ],
            }
        )

        jlu._render_results_html(tmp_path, "h", datetime(2026, 5, 6))
        content = (tmp_path / "Results.html").read_text()

        assert "1 ok" in content
        assert "1 warning" in content
        assert "1 failed" in content
