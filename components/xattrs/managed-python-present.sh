#!/bin/bash
#
# Checks if Managed Python build is present on endpoints
#
# Returns "Present" if binary is present "Missing" otherwise

managed_python="/usr/local/bin/managed_python3"

if [[ -e "$managed_python" ]]; then
	echo "<result>Present</result>"
else
	echo "<result>Missing</result>"
fi
