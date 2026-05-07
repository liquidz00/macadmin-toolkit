#!/usr/local/bin/managed_python3
"""
Default Dock Configuration script (docklib).

Configures the active console user's Dock using the docklib package,
which ships in macadmins managed_python3 builds. Adds Self Service,
Chrome, Slack, Zoom; optionally adds a custom app path via $5.

The companion default_dock.py uses dockutil instead. Pick whichever
fits your fleet's existing tooling.

Caveats:
    - docklib reads/writes the dock plist directly. cfprefsd may have
      a cached copy in memory; restarting the Dock as the affected
      user (done at the end of this script) flushes the per-app cache.
      If you hit ordering issues, kill cfprefsd as that user too.
    - Targets the *console* user, so trigger this script with a
      recurring check-in, login, or self-service policy after a user
      session is established.

Written 05/07/2026 — Andrew Lerman (@liquidz00)

Parameter Reference:
    - $4: Dry-run (True/False): If True, outputs what would be added.
          Defaults to False.
    - $5: Custom app path: If provided, adds the application at the
          given path to the dock alongside the defaults.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from docklib import Dock
from pymdm import MdmLogger, ParamParser, SystemInfo

SCRIPT_NAME = Path(__file__).name
VERSION = "1.0.0"

DEFAULT_APPS: tuple[str, ...] = (
    "/Applications/Self Service.app",
    "/Applications/Google Chrome.app",
    "/Applications/Slack.app",
    "/Applications/zoom.us.app",
)

logger = MdmLogger()


def main() -> None:
    logger.log_startup(SCRIPT_NAME, VERSION)

    dry_run = ParamParser.get_bool(4)
    extra_app = ParamParser.get(5)

    console_user = SystemInfo.get_console_user()
    if console_user is None:
        logger.warn("No console user; cannot configure dock")
        return
    username, _, home = console_user

    dock_plist = home / "Library" / "Preferences" / "com.apple.dock.plist"
    dock = Dock(filename=str(dock_plist))

    apps = list(DEFAULT_APPS)
    if extra_app:
        apps.append(extra_app)

    for app in apps:
        if not Path(app).exists():
            logger.warn(f"App not found, skipping: {app}")
            continue
        label = Path(app).stem
        if dock.findExistingLabel(label, section="persistent-apps") > -1:
            logger.info(f"Already in dock, skipping: {app}")
            continue
        if dry_run:
            logger.info(f"Would add to dock: {app}")
            continue
        item = dock.makeDockAppEntry(app)
        dock.items["persistent-apps"].append(item)
        logger.info(f"Added to dock: {app}")

    if not dry_run:
        dock.save()
        subprocess.run(["/usr/bin/killall", "-u", username, "Dock"], check=False)
        logger.info(f"Restarted Dock for {username}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.log_exception(f"{SCRIPT_NAME} failed", exc, exit_code=1)
