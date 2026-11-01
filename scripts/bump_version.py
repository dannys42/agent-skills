#!/usr/bin/env python3
"""Set one plugin's version everywhere it is written.

    scripts/bump_version.py <plugin> <version>     e.g. scripts/bump_version.py task-workflow 0.17.2

Updates the plugin's four manifests, its entry in .claude-plugin/marketplace.json, and every
metrics stamp in its skills (`<skill-name> <old version>`, as in `skill` `tasklist-run 0.17.1`).
Prints each file it changed. tests/test_plugin_layout.py checks the result. The CHANGELOG entry
and the ledger rows stay manual: they need words, not a number.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = (".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json", "gemini-extension.json")
VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def main(argv):
    if len(argv) != 3 or not VERSION.match(argv[2]):
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    plugin, new = argv[1], argv[2]
    base = ROOT / "plugins" / plugin
    if not (base / MANIFESTS[0]).is_file():
        print(f"no plugin named {plugin}", file=sys.stderr)
        return 1
    old = json.loads((base / MANIFESTS[0]).read_text(encoding="utf-8"))["version"]
    if old == new:
        print(f"{plugin} is already {new}", file=sys.stderr)
        return 1

    # Work out every rewrite first, so a failure leaves nothing half bumped.
    edits = {}
    for relative in MANIFESTS:
        path = base / relative
        text = path.read_text(encoding="utf-8")
        edits[path] = re.sub(r'("version":\s*")' + re.escape(old) + '"', r"\g<1>" + new + '"', text, count=1)
        if json.loads(edits[path]).get("version") != new:
            print(f"{path.relative_to(ROOT)} is not at {old}", file=sys.stderr)
            return 1

    market = ROOT / ".claude-plugin" / "marketplace.json"
    text = market.read_text(encoding="utf-8")
    entry = re.search(r'"name":\s*"' + re.escape(plugin) + r'",(?:(?!"name":)[\s\S])*?"version":\s*"' + re.escape(old) + '"', text)
    if entry:
        edits[market] = text[: entry.start()] + entry.group(0)[: -len(old) - 1] + new + '"' + text[entry.end():]
    if not entry or [e["version"] for e in json.loads(edits[market])["plugins"] if e["name"] == plugin] != [new]:
        print(f"marketplace entry for {plugin} at {old} not found", file=sys.stderr)
        return 1

    skills = sorted((p.name for p in (base / "skills").iterdir() if p.is_dir()), key=len, reverse=True)
    stamp = re.compile(r"(?<![\w-])(" + "|".join(map(re.escape, skills)) + r") " + re.escape(old) + r"(?![\d.]*\d)")
    for path in sorted((base / "skills").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        edits[path] = stamp.sub(lambda m: f"{m.group(1)} {new}", text)

    changed = []
    for path, text in edits.items():
        if path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
            changed.append(path.relative_to(ROOT))

    print(f"{plugin}: {old} -> {new}")
    for path in changed:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
