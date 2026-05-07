#!/usr/local/bin/managed_python3
"""
Default Dock Configuration script (dockutil).

Configures the active console user's Dock with the org's standard set
of applications: Self Service, Chrome, Slack, Zoom. Optionally adds a
custom app path via $5.

Implementation uses dockutil (https://github.com/kcrawford/dockutil),
which must be installed at /usr/local/bin/dockutil. The companion
default_dock_docklib.py uses the docklib Python package instead.

Written 05/05/2026 — Andrew Lerman (@liquidz00)

Parameter Reference:
    - $4: Dry-run (True/False): If True, outputs what would be added.
          Defaults to False.
    - $5: Custom app path: If provided, adds the application at the
          given path to the dock alongside the defaults.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from pymdm import MdmLogger, ParamParser, SystemInfo

SCRIPT_NAME = Path(__file__).name
VERSION = "1.0.0"
DOCKUTIL = "/usr/local/bin/dockutil"

DEFAULT_APPS: tuple[str, ...] = (
    "/Applications/Self Service.app",
    "/Applications/Google Chrome.app",
    "/Applications/Slack.app",
    "/Applications/zoom.us.app",
)

logger = MdmLogger()


def add_to_dock(app_path: str, username: str, dry_run: bool) -> None:
    if not Path(app_path).exists():
        logger.warn(f"App not found, skipping: {app_path}")
        return
    if dry_run:
        logger.info(f"Would add to dock: {app_path}")
        return
    cmd = [DOCKUTIL, "--add", app_path, "--no-restart", "--user", username]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warn(f"dockutil failed for {app_path}: {result.stderr.strip()}")
    else:
        logger.info(f"Added to dock: {app_path}")


def main() -> None:
    logger.log_startup(SCRIPT_NAME, VERSION)

    if not Path(DOCKUTIL).exists():
        logger.error(f"dockutil not found at {DOCKUTIL}; install before running", exit_code=1)
        return

    dry_run = ParamParser.get_bool(4)
    extra_app = ParamParser.get(5)

    console_user = SystemInfo.get_console_user()
    if console_user is None:
        logger.warn("No console user; cannot configure dock")
        return
    username, _, _ = console_user

    apps = list(DEFAULT_APPS)
    if extra_app:
        apps.append(extra_app)

    for app in apps:
        add_to_dock(app, username, dry_run)

    if not dry_run:
        subprocess.run(["/usr/bin/killall", "-u", username, "Dock"], check=False)
        logger.info(f"Restarted Dock for {username}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.log_exception(f"{SCRIPT_NAME} failed", exc, exit_code=1)
