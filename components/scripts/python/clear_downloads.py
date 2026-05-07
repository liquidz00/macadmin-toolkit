#!/usr/local/bin/managed_python3
"""
Clear Downloads folder script.

Removes all contents of the active console user's `~/Downloads` directory.
Designed for weekly weekend execution via Jamf policy. Does NOT filter
by file age; every item gets deleted on each run.

Written 05/07/2026 — Andrew Lerman (@liquidz00)

Parameter Reference:
    - $4: Dry-run (True/False): If True, logs what would be removed
          without deleting. Defaults to False.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pymdm import MdmLogger, ParamParser, SystemInfo

SCRIPT_NAME = Path(__file__).name
VERSION = "1.0.0"

logger = MdmLogger()


def main() -> None:
    logger.log_startup(SCRIPT_NAME, VERSION)

    dry_run = ParamParser.get_bool(4)
    if dry_run:
        logger.info("Dry-run mode: no files will be deleted")

    console_user = SystemInfo.get_console_user()
    if console_user is None:
        logger.warn("No console user; nothing to clear")
        return
    username, _, home = console_user

    downloads = home / "Downloads"
    if not downloads.exists():
        logger.warn(f"{downloads} does not exist")
        return

    items = list(downloads.iterdir())
    logger.info(f"Found {len(items)} item(s) in {downloads} for {username}")

    removed = 0
    for item in items:
        if dry_run:
            logger.info(f"Would remove: {item}")
            continue
        try:
            if item.is_dir() and not item.is_symlink():
                shutil.rmtree(item)
            else:
                item.unlink()
            removed += 1
        except OSError as exc:
            logger.warn(f"Failed to remove {item}: {exc}")

    if not dry_run:
        logger.info(f"Removed {removed} of {len(items)} item(s)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.log_exception(f"{SCRIPT_NAME} failed", exc, exit_code=1)
