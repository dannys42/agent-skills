#!/bin/sh
# Prints the rung cycle's next step (`roadmap next`) into the /rung skill as it loads.
# Always exits 0, because a failed injected command aborts the skill; never builds, because
# a first build can outlast the injection timeout. The skill installs the tool when this says so.
# `min` is the oldest tool version this plugin needs; a newer one is fine.
b=${XDG_CACHE_HOME:-$HOME/.cache}/danny-agent-skills/bin/roadmap
min=0.7.0
v=$("$b" --version 2>/dev/null)
if [ -z "$v" ] || [ "$(printf '%s\n%s\n' "$min" "$v" | sort -t. -k1,1n -k2,2n -k3,3n | head -n 1)" != "$min" ]; then
  echo "roadmap: missing or older than $min"
  exit 0
fi
"$b" next "$@" 2>&1
exit 0
