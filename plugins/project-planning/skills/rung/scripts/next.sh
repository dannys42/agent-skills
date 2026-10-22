#!/bin/sh
# Prints the rung cycle's next step (`roadmap next`) into the /rung skill as it loads.
# Always exits 0, because a failed injected command aborts the skill; never builds, because
# a first build can outlast the injection timeout. The skill installs the tool when this says so.
b=${XDG_CACHE_HOME:-$HOME/.cache}/danny-agent-skills/bin/roadmap
if [ "$("$b" --version 2>/dev/null)" != "0.5.0" ]; then
  echo "roadmap: missing or not 0.5.0"
  exit 0
fi
"$b" next "$@" 2>&1
exit 0
