#!/usr/local/bin/managed_python3
"""
Extension attribute — Falcon Sensor loaded state.

Reports whether the CrowdStrike Falcon Sensor system extension is
currently loaded on the device. Sources the value from `falconctl info`
(output is a plist) and surfaces the `sensor_loaded` field directly.

Output:
    True              — sensor is loaded and active.
    False             — sensor is installed but not loaded (degraded).
    Agent not found   — Falcon.app is not present at the expected path.
    Error: ...        — falconctl call or plist parse failed.

Written 05/07/2026 — Andrew Lerman (@liquidz00)
"""

import plistlib
import subprocess
from pathlib import Path

falcon_path = Path("/Applications/Falcon.app/Contents/Resources/falconctl")

if falcon_path.exists():
    try:
        falcon_info = plistlib.loads(subprocess.check_output([falcon_path, "info"]))
        sensor_state = str(falcon_info.get("sensor_loaded", ""))
    except Exception as e:
        sensor_state = f"Error: {type(e).__name__} retrieving sensor state: {e}"
else:
    sensor_state = "Agent not found"

print(f"<result>{sensor_state}</result>")
