#!/bin/sh
# Build the plan tools with SwiftPM and install copies outside PATH, in a cache directory:
#   ${XDG_CACHE_HOME:-~/.cache}/danny-agent-skills/bin/{tasklist,roadmap}
# Run those binaries by full path, never through `swift run`. Rebuilds only when the sources are
# newer than the built binary; copies only when the installed version differs from the built one.
# The cache can be deleted at any time: the next run rebuilds it. The first build fetches
# swift-argument-parser (network or SwiftPM cache).
#   build.sh            build if needed, install, print the install directory
set -eu
command -v swift >/dev/null 2>&1 || { echo "swift not found on PATH; the plan tools are optional, apply the rules by hand" >&2; exit 1; }
here=$(cd "$(dirname "$0")" && pwd)
cd "$here"
built=.build/release
if [ ! -x "$built/tasklist" ] || [ -n "$(find Package.swift Sources -type f -newer "$built/tasklist" | head -n 1)" ]; then
  swift build -c release >&2
  touch "$built/tasklist" "$built/roadmap"
fi
dir=${XDG_CACHE_HOME:-$HOME/.cache}/danny-agent-skills/bin
mkdir -p "$dir"
for tool in tasklist roadmap; do
  if [ "$("$dir/$tool" --version 2>/dev/null || true)" != "$("$built/$tool" --version)" ] || [ "$built/$tool" -nt "$dir/$tool" ]; then
    cp "$built/$tool" "$dir/$tool.tmp" && mv "$dir/$tool.tmp" "$dir/$tool"
  fi
done
echo "$dir"
