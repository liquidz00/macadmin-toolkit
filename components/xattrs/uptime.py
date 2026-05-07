#!/usr/local/bin/managed_python3
"""
Extension attribute — system uptime.

Reports the number of whole days since the device's last boot, parsed
from `sysctl kern.boottime`. Useful for surfacing devices that have
skipped reboot cycles and may be carrying pending OS or app updates.

Output:
    Whole number of days since boot as a string (e.g. "7"). "0" if
    booted within the last 24h. Error string if `sysctl` output cannot
    be parsed.

    Configure the EA's data type as Integer in Jamf so the value sorts
    and filters numerically.

Written 05/07/2026 — Andrew Lerman (@liquidz00)
"""

import re
import subprocess
import time

try:
    output = subprocess.check_output(["/usr/sbin/sysctl", "-n", "kern.boottime"], text=True)
    match = re.search(r"sec = (\d+)", output)
    if not match:
        result = "Error: could not parse boottime"
    else:
        days = int((time.time() - int(match.group(1))) // 86400)
        result = str(days)
except Exception as exc:
    result = f"Error: {type(exc).__name__}"

print(f"<result>{result}</result>")
