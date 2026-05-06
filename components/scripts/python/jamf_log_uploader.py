#!/usr/local/bin/managed_python3
"""
Jamf log uploader script.

Collects relevant Jamf, system, networking, and SSO logs into a compressed
archive and uploads it to a webhook. Falls back to /Users/Shared/ when the
archive exceeds the webhook size cap or no webhook URL is provided.

Written 05/05/2026 — Andrew Lerman (@liquidz00)

Parameter Reference:
    - $4: Webhook URL: HTTP endpoint to upload the archive to. Falls back to
          /Users/Shared/ if absent.
    - $5: Dry-run (True/False): If True, skips webhook upload and preserves
          the unzipped working directory. Defaults to False.
    - $6: Custom subsystem (optional): Extra subsystem identifier to capture
          unified logs for (e.g. "com.jamf.protect").
    - $7: Custom subsystem (optional): Same as $6.
    - $8: Custom subsystem (optional): Same as $6.
"""

from __future__ import annotations

import html
import plistlib
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from pymdm import CommandRunner, MdmLogger, ParamParser, SystemInfo, WebhookSender

__version__ = "1.0.0"
SCRIPT_NAME = "jamf_log_uploader.py"

# MDM enrollment profile UUID — replace with your org's value (see `profiles -L`).
MDM_PROFILE_UUID = "REPLACE-WITH-YOUR-MDM-PROFILE-UUID"

# Webhook size cap; archives larger than this fall back to /Users/Shared/.
WEBHOOK_MAX_BYTES = 10 * 1024 * 1024

# SSO log capture window: 15 minutes before enrollment, 20 minutes after.
ENROLLMENT_WINDOW_BEFORE = timedelta(minutes=15)
ENROLLMENT_WINDOW_AFTER = timedelta(minutes=20)

# Subsystem predicates collected into the SSO/ subdirectory.
DEFAULT_SSO_SUBSYSTEMS: tuple[str, ...] = (
    "com.apple.AppSSOAgent",
    "com.apple.AppSSO",
    "com.okta.mobile",
    "com.okta.deviceaccess",
)

FALLBACK_OUTPUT_DIR = Path("/Users/Shared")

logger = MdmLogger()

# step name -> list of {"target": ..., "status": "ok"|"warn"|"fail", "message": ...}
RESULTS: dict[str, list[dict[str, str]]] = {}


def _record(step: str, target: str, status: str, message: str = "") -> None:
    """Append a collection result for the Results.html summary."""
    RESULTS.setdefault(step, []).append({"target": target, "status": status, "message": message})


def _ensure_dir(path: Path) -> Path:
    """Create a directory (and parents) if missing; return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_copy(src: Path, dest_dir: Path, step: str) -> None:
    """Copy ``src`` into ``dest_dir`` if it exists; warn-and-skip otherwise."""
    if not src.exists():
        logger.warn(f"Source not found, skipping: {src}")
        _record(step, str(src), "warn", "not found")
        return
    try:
        shutil.copy2(src, dest_dir / src.name)
        logger.info(f"Copied {src}")
        _record(step, str(src), "ok")
    except OSError as exc:
        logger.warn(f"Failed to copy {src}: {exc}")
        _record(step, str(src), "fail", str(exc))


def _save_command_output(
    runner: CommandRunner,
    command: list[str],
    dest: Path,
    step: str,
    timeout: int = 60,
    as_user: bool = False,
) -> None:
    """Run a command and save stdout (+stderr if any) to ``dest``. Records result."""
    cmd_str = " ".join(command)
    try:
        if as_user:
            result = runner.run_as_user(command, timeout=timeout, check=False)
        else:
            result = runner.run(command, timeout=timeout, check=False)
    except Exception as exc:
        logger.warn(f"Failed to run {cmd_str}: {exc}")
        _record(step, cmd_str, "fail", str(exc))
        return

    status = "ok" if result.returncode == 0 else "warn"
    message = "" if result.returncode == 0 else f"exit code {result.returncode}"
    if result.returncode != 0:
        logger.warn(f"Command exited {result.returncode}: {cmd_str}")

    body = result.stdout
    if result.stderr:
        body += "\n--- STDERR ---\n" + result.stderr
    try:
        dest.write_text(body)
        logger.info(f"Saved output to {dest.name}")
    except OSError as exc:
        logger.warn(f"Failed to write {dest}: {exc}")
        _record(step, cmd_str, "fail", f"write error: {exc}")
        return

    _record(step, cmd_str, status, message)


def _get_mdm_enrollment_date(runner: CommandRunner) -> datetime | None:
    """Look up the install date of the MDM profile matching ``MDM_PROFILE_UUID``."""
    try:
        xml = runner.run(
            ["system_profiler", "-xml", "SPConfigurationProfileDataType"],
            timeout=60,
        )
    except Exception as exc:
        logger.warn(f"system_profiler failed: {exc}")
        return None

    try:
        data = plistlib.loads(xml.encode("utf-8"))
    except plistlib.InvalidFileException as exc:
        logger.warn(f"Could not parse system_profiler output: {exc}")
        return None

    for top in data:
        for profile in top.get("_items", []):
            if profile.get("spconfigprofile_uuid") != MDM_PROFILE_UUID:
                continue
            install = profile.get("spconfigprofile_install_date")
            if isinstance(install, datetime):
                return install
            if isinstance(install, str):
                try:
                    return datetime.fromisoformat(install.replace("Z", "+00:00"))
                except ValueError:
                    logger.warn(f"Unparseable install date: {install!r}")
                    return None

    logger.warn(f"MDM profile {MDM_PROFILE_UUID} not present in system_profiler output")
    return None


def _collect_jamf(working_dir: Path, runner: CommandRunner) -> None:
    """Collect Jamf-specific artifacts."""
    step = "Jamf"
    jamf_dir = _ensure_dir(working_dir / step)

    _safe_copy(Path("/private/var/log/jamf.log"), jamf_dir, step)
    _safe_copy(Path("/Library/Preferences/com.jamfsoftware.jamf.plist"), jamf_dir, step)
    _safe_copy(Path("/Library/Logs/MCXTools.log"), jamf_dir, step)

    recon_tmp = Path("/Library/Application Support/JAMF/tmp")
    if recon_tmp.exists():
        try:
            shutil.copytree(recon_tmp, jamf_dir / "tmp", dirs_exist_ok=True)
            logger.info(f"Copied {recon_tmp}")
            _record(step, str(recon_tmp), "ok")
        except OSError as exc:
            logger.warn(f"Failed to copy {recon_tmp}: {exc}")
            _record(step, str(recon_tmp), "fail", str(exc))

    _save_command_output(
        runner,
        ["/usr/libexec/mdmclient", "QueryInstalledProfiles"],
        jamf_dir / "mdmclient_profiles.txt",
        step,
    )
    _save_command_output(
        runner,
        ["/usr/bin/profiles", "-L", "-output", "stdout"],
        jamf_dir / "profiles_list.txt",
        step,
    )


def _collect_system(working_dir: Path, runner: CommandRunner) -> None:
    """Collect general macOS artifacts."""
    step = "System"
    system_dir = _ensure_dir(working_dir / step)

    _safe_copy(Path("/var/log/install.log"), system_dir, step)
    _safe_copy(Path("/var/log/system.log"), system_dir, step)

    _save_command_output(
        runner,
        ["/usr/sbin/system_profiler", "-xml"],
        system_dir / "system_profiler.xml",
        step,
        timeout=300,
    )
    _save_command_output(
        runner,
        ["/bin/launchctl", "dumpstate"],
        system_dir / "launchctl_dumpstate.txt",
        step,
        timeout=120,
    )
    _save_command_output(
        runner,
        ["/usr/bin/systemextensionsctl", "list"],
        system_dir / "system_extensions.txt",
        step,
    )
    _save_command_output(runner, ["/usr/sbin/kextstat"], system_dir / "kextstat.txt", step)


def _collect_network(working_dir: Path, runner: CommandRunner) -> None:
    """Collect network configuration and connectivity diagnostics."""
    step = "Networking"
    net_dir = _ensure_dir(working_dir / step)

    _save_command_output(
        runner,
        ["/usr/sbin/networksetup", "-listallnetworkservices"],
        net_dir / "network_services.txt",
        step,
    )
    _save_command_output(runner, ["/sbin/ifconfig"], net_dir / "ifconfig.txt", step)
    _save_command_output(runner, ["/usr/sbin/scutil", "--dns"], net_dir / "scutil_dns.txt", step)
    _save_command_output(
        runner, ["/sbin/route", "-n", "get", "default"], net_dir / "default_route.txt", step
    )
    _save_command_output(
        runner,
        ["/usr/sbin/system_profiler", "SPNetworkDataType"],
        net_dir / "system_profiler_network.txt",
        step,
    )
    _save_command_output(
        runner,
        ["/sbin/ping", "-c", "3", "8.8.8.8"],
        net_dir / "ping_google_dns.txt",
        step,
        timeout=30,
    )
    _save_command_output(
        runner,
        ["/sbin/ping", "-c", "3", "1.1.1.1"],
        net_dir / "ping_cloudflare_dns.txt",
        step,
        timeout=30,
    )
    _save_command_output(
        runner,
        ["/usr/bin/networkQuality", "-v"],
        net_dir / "network_quality.txt",
        step,
        timeout=120,
    )


def _collect_sso(
    working_dir: Path,
    runner: CommandRunner,
    enrollment_date: datetime | None,
) -> None:
    """Collect Platform SSO, AppSSO, and Okta-related logs."""
    # `app-sso` returns user-scoped state; running as root produces (null) results.
    # The runner is initialized with the console user's identity so run_as_user
    # routes through `launchctl asuser` + `sudo -u` to get accurate output.
    step = "SSO"
    sso_dir = _ensure_dir(working_dir / step)

    _save_command_output(
        runner,
        ["/usr/bin/app-sso", "platform", "-s"],
        sso_dir / "platform_sso_state.txt",
        step,
        as_user=True,
    )
    _save_command_output(
        runner, ["/usr/bin/app-sso", "list"], sso_dir / "appsso_list.txt", step, as_user=True
    )

    console_user = SystemInfo.get_console_user()
    if console_user:
        _, _, home = console_user
        okta_verify_logs = home / "Library" / "Logs" / "Okta Verify"
        if okta_verify_logs.exists():
            try:
                shutil.copytree(okta_verify_logs, sso_dir / "okta_verify_logs", dirs_exist_ok=True)
                logger.info(f"Copied {okta_verify_logs}")
                _record(step, str(okta_verify_logs), "ok")
            except OSError as exc:
                logger.warn(f"Failed to copy Okta Verify logs: {exc}")
                _record(step, str(okta_verify_logs), "fail", str(exc))

    if enrollment_date is None:
        logger.warn("Enrollment date unavailable; using last 30m for SSO unified logs")
        start = datetime.now() - timedelta(minutes=30)
        end = datetime.now()
    else:
        start = enrollment_date - ENROLLMENT_WINDOW_BEFORE
        end = enrollment_date + ENROLLMENT_WINDOW_AFTER

    predicate = " OR ".join(f'subsystem == "{s}"' for s in DEFAULT_SSO_SUBSYSTEMS)
    log_show_cmd = [
        "/usr/bin/log",
        "show",
        "--start",
        start.strftime("%Y-%m-%d %H:%M:%S"),
        "--end",
        end.strftime("%Y-%m-%d %H:%M:%S"),
        "--predicate",
        predicate,
        "--info",
    ]
    _save_command_output(runner, log_show_cmd, sso_dir / "sso_unified_logs.txt", step, timeout=180)


def _collect_custom_app(
    working_dir: Path,
    runner: CommandRunner,
    subsystem: str,
) -> None:
    """Capture unified logs for a single user-supplied subsystem identifier."""
    safe_name = subsystem.replace(".", "_")
    step = f"CustomApp:{subsystem}"
    custom_dir = _ensure_dir(working_dir / f"CustomApp_{safe_name}")

    log_show_cmd = [
        "/usr/bin/log",
        "show",
        "--last",
        "24h",
        "--predicate",
        f'subsystem == "{subsystem}"',
        "--info",
    ]
    _save_command_output(
        runner, log_show_cmd, custom_dir / f"{safe_name}_unified_logs.txt", step, timeout=180
    )


def _render_results_html(working_dir: Path, hostname: str, started_at: datetime) -> None:
    """Render Results.html in the Jamf log-grabber visual style.

    Uses the upstream's color palette and structural conventions: dark gray
    background, Helvetica, h1 in blue, h2 in teal, inline code blocks with
    color-coded status indicators per entry.
    """
    # Palette mirrors the upstream Jamf script: green = success, orange =
    # warning, red = critical/failure. The remaining upstream colors (yellow,
    # lime, white) aren't surfaced because our status taxonomy is three-state.
    color = {
        "ok": "#37bb9a",
        "warn": "#ffa500",
        "fail": "#ff4136",
    }

    sections: list[str] = []
    for step, entries in RESULTS.items():
        ok_count = sum(1 for e in entries if e["status"] == "ok")
        warn_count = sum(1 for e in entries if e["status"] == "warn")
        fail_count = sum(1 for e in entries if e["status"] == "fail")

        rows: list[str] = []
        for entry in entries:
            status = entry["status"]
            msg = f" — {html.escape(entry['message'])}" if entry["message"] else ""
            rows.append(
                f'<code style="color:{color[status]};">'
                f"[{status.upper()}] {html.escape(entry['target'])}{msg}<br></code>"
            )

        sections.append(
            f"<h2>{html.escape(step)}</h2>\n"
            f'<p class="summary">{ok_count} ok &middot; '
            f"{warn_count} warning &middot; {fail_count} failed</p>\n"
            f'<div class="entries">{"".join(rows)}</div>'
        )

    body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Log Grabber Results — {html.escape(hostname)}</title>
<style>
body {{ background-color:#444444; font-family:Helvetica,Arial,sans-serif; margin:20px; color:#dddddd; }}
h1 {{ color:#9eb8d5; }}
h2, h3, h4 {{ color:#37bb9a; }}
code {{ font-family:'SF Mono', Menlo, monospace; font-size:0.92em; line-height:1.6; }}
.meta {{ color:#aaaaaa; margin:0.25rem 0; }}
.summary {{ color:#cccccc; font-size:0.9em; margin:0 0 0.5rem 0; }}
.entries {{ margin-bottom:1.5rem; }}
hr {{ border:none; border-top:1px solid #555555; margin:1.5rem 0; }}
</style>
</head>
<body>
<h1>Log Grabber Results</h1>
<p class="meta">Host: {html.escape(hostname)}</p>
<p class="meta">Started: {started_at.isoformat(timespec="seconds")}</p>
<p class="meta">Script: {SCRIPT_NAME} v{__version__}</p>
<hr>
{"".join(sections)}
</body>
</html>
"""
    (working_dir / "Results.html").write_text(body)
    logger.info("Generated Results.html")


def _compress(working_dir: Path) -> Path:
    """Zip ``working_dir`` next to itself; return the archive path."""
    archive_base = working_dir.with_suffix("")
    archive_str = shutil.make_archive(str(archive_base), "zip", root_dir=working_dir)
    archive_path = Path(archive_str)
    logger.info(f"Archive created: {archive_path} ({archive_path.stat().st_size:,} bytes)")
    return archive_path


def _send_or_save(
    archive: Path,
    webhook_url: str | None,
    metadata: dict[str, str],
    dry_run: bool,
) -> Path:
    """Upload to webhook if conditions allow; otherwise save under /Users/Shared/."""
    size = archive.stat().st_size

    if dry_run:
        logger.info("Dry-run: skipping webhook upload")
    elif not webhook_url:
        logger.info("No webhook URL provided; saving locally")
    elif size > WEBHOOK_MAX_BYTES:
        logger.warn(
            f"Archive {size:,} bytes exceeds webhook cap {WEBHOOK_MAX_BYTES:,}; saving locally"
        )
    else:
        sender = WebhookSender(url=webhook_url, logger=logger, logfile=archive)
        if sender.send_logfile(**metadata):
            logger.info("Upload succeeded; cleanup retains local archive copy")
            return archive
        logger.warn("Upload failed; falling back to local save")

    _ensure_dir(FALLBACK_OUTPUT_DIR)
    final = FALLBACK_OUTPUT_DIR / archive.name
    shutil.copy2(archive, final)
    logger.info(f"Saved archive to {final}")
    return final


def main() -> None:
    """Orchestrate parameter parsing, log collection, compression, and upload."""
    started_at = datetime.now()
    logger.log_startup(SCRIPT_NAME, __version__)

    webhook_url = ParamParser.get(4)
    dry_run = ParamParser.get_bool(5)
    custom_subsystems = [
        s for s in (ParamParser.get(6), ParamParser.get(7), ParamParser.get(8)) if s
    ]

    logger.info(f"Webhook configured: {bool(webhook_url)}")
    logger.info(f"Dry-run: {dry_run}")
    if custom_subsystems:
        logger.info(f"Custom subsystems: {custom_subsystems}")

    console_user = SystemInfo.get_console_user()
    if console_user is None:
        logger.warn("No console user detected; SSO collection will be limited")
        username, uid = None, None
    else:
        username, uid, _ = console_user
        logger.info(f"Console user: {username} (uid={uid})")

    runner = CommandRunner(logger=logger, username=username, uid=uid)

    hostname = SystemInfo.get_hostname()
    today = started_at.strftime("%Y-%m-%d")
    working_dir = _ensure_dir(Path("/tmp") / f"{hostname}_{today}_logs")
    logger.info(f"Working directory: {working_dir}")

    enrollment_date = _get_mdm_enrollment_date(runner)
    if enrollment_date:
        logger.info(f"MDM enrollment date: {enrollment_date.isoformat()}")

    _collect_jamf(working_dir, runner)
    _collect_system(working_dir, runner)
    _collect_network(working_dir, runner)
    if username and uid:
        _collect_sso(working_dir, runner, enrollment_date)
    for subsystem in custom_subsystems:
        _collect_custom_app(working_dir, runner, subsystem)

    _render_results_html(working_dir, hostname, started_at)

    archive = _compress(working_dir)

    metadata = {
        "hostname": hostname,
        "username": username or "unknown",
        "script_name": SCRIPT_NAME,
        "script_version": __version__,
    }
    final_path = _send_or_save(archive, webhook_url, metadata, dry_run=dry_run)

    if not dry_run:
        try:
            shutil.rmtree(working_dir)
            logger.info(f"Cleaned up working directory {working_dir}")
        except OSError as exc:
            logger.warn(f"Could not remove working directory {working_dir}: {exc}")

    logger.info(f"Done. Final archive: {final_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.log_exception(f"{SCRIPT_NAME} failed", exc, exit_code=1)
