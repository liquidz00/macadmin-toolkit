#!/usr/local/bin/managed_python3
"""
Extension attribute — Falcon Sensor agent ID.

Reports the CrowdStrike Falcon Sensor agent ID (AID) for the device.
Sources the value from `falconctl info` (output is a plist), and
formats the raw 32-character hex string into the canonical UUID form
(8-4-4-4-12) for readability in Jamf inventory.

Output:
    UUID string         — agent ID in canonical UUID format.
    No Agent ID found   — falconctl returned, but the `aid` key was
                          missing or not a valid hex string.
    Agent not found     — Falcon.app is not present at the expected
                          path.

Written 05/07/2026 — Andrew Lerman (@liquidz00)
"""

import plistlib
import subprocess
import uuid
from pathlib import Path

falcon_path = Path("/Applications/Falcon.app/Contents/Resources/falconctl")

if falcon_path.exists():
    falcon_info = plistlib.loads(subprocess.check_output([falcon_path, "info"]))
    agent_id = falcon_info.get("aid", "")
    if agent_id:
        try:
            aid = str(uuid.UUID(hex=agent_id))
        except ValueError:
            aid = "No Agent ID found"
    else:
        aid = "No Agent ID found"
else:
    aid = "Agent not found"

print(f"<result>{aid}</result>")
