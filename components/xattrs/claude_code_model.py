#!/usr/local/bin/managed_python3
"""
Extension attribute — Claude Code configured model.

Reads the active console user's `~/.claude/settings.json` and reports
the configured model (e.g. "opus", "sonnet"). Returns the literal value
written in settings; if no `model` key is present, returns "Default"
(which is what Claude Code falls back to when the field is unset).

Output:
    The configured model string, "Default" if unset, "Not configured"
    if `settings.json` does not exist, "No user logged in" if no console
    user is present, or an error string.

Written 05/07/2026 — Andrew Lerman (@liquidz00)
"""

import json

from pymdm import SystemInfo

try:
    console_user = SystemInfo.get_console_user()
    if console_user is None:
        result = "No user logged in"
    else:
        _, _, home = console_user
        settings_path = home / ".claude" / "settings.json"
        if not settings_path.exists():
            result = "Not configured"
        else:
            data = json.loads(settings_path.read_text())
            result = data.get("model", "Default")
except Exception as exc:
    result = f"Error: {type(exc).__name__}"

print(f"<result>{result}</result>")
