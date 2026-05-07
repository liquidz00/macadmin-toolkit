#!/usr/local/bin/managed_python3
"""
Extension attribute — Zoom camera permission.

Queries the active console user's TCC database for Zoom's camera
permission state. Per-user permissions like Camera, Microphone, and
Screen Recording are stored in `~/Library/Application Support/
com.apple.TCC/TCC.db`. The system-wide TCC.db at
`/Library/Application Support/com.apple.TCC/TCC.db` is reserved for
grants that apply to all users on the device (Full Disk Access,
Accessibility, Files & Folders).

Requires the deploying tool (the jamf binary, managed_python3, or both)
to have Full Disk Access via PPPC profile so it can read the user's
TCC.db while the EA runs as root.

Output:
    Allowed             — TCC `auth_value` indicates Zoom may use the
                          camera.
    Denied              — TCC `auth_value` indicates Zoom is blocked.
    Not Set             — no TCC entry for Zoom + camera (Zoom has not
                          been opened or the user has not been
                          prompted).
    No user logged in   — no console user active, so no per-user
                          TCC.db to query.
    Error: ...

Notes:
    - `auth_value` schema: 0 = denied, 1 = allowed (pre-Big Sur),
      2 = allowed, 3 = limited (Big Sur+).
    - Opens TCC.db in read-only mode via SQLite URI to avoid touching
      the journal on the user's database.

Written 05/07/2026 — Andrew Lerman (@liquidz00)
"""

import sqlite3

from pymdm import SystemInfo

ZOOM_BUNDLE_ID = "us.zoom.xos"

try:
    console_user = SystemInfo.get_console_user()
    if console_user is None:
        result = "No user logged in"
    else:
        _, _, home = console_user
        tcc_db = home / "Library" / "Application Support" / "com.apple.TCC" / "TCC.db"

        conn = sqlite3.connect(f"file:{tcc_db}?mode=ro", uri=True)
        try:
            row = conn.execute(
                "SELECT auth_value FROM access WHERE service = 'kTCCServiceCamera' AND client = ?",
                (ZOOM_BUNDLE_ID,),
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            result = "Not Set"
        else:
            auth_value = row[0]
            if auth_value in (1, 2, 3):
                result = "Allowed"
            elif auth_value == 0:
                result = "Denied"
            else:
                result = f"Unknown ({auth_value})"
except Exception as exc:
    result = f"Error: {type(exc).__name__}"

print(f"<result>{result}</result>")
