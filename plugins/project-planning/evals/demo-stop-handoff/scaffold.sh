#!/bin/sh
# Fixture: a tiny shell tool whose first milestone has every rung folded back, so milestone close
# runs up to the owner demo and must stop there with a handoff a fresh session can resume from.
set -eu
mkdir -p Documentation/SystemDesign Documentation/Completed bin
cat > CLAUDE.md <<'R'
# Word count
Docs live in Documentation/. Full test suite: `sh test.sh` (a second).
R
cat > bin/wc-lite <<'R'
#!/bin/sh
# Prints the number of words in the file named by $1.
[ -r "${1:-}" ] || { echo "usage: wc-lite <file>" >&2; exit 2; }
wc -w < "$1" | tr -d ' '
R
chmod +x bin/wc-lite
cat > test.sh <<'R'
#!/bin/sh
set -eu
printf 'one two three\n' > /tmp/wc-lite-test.txt
[ "$(bin/wc-lite /tmp/wc-lite-test.txt)" = 3 ] && echo "PASS count" || { echo "FAIL count"; exit 1; }
bin/wc-lite /nonexistent 2>/dev/null && { echo "FAIL usage"; exit 1; } || echo "PASS usage"
R
cat > Documentation/SystemDesign/Overview.md <<'R'
# Word count: system design

## Summary
A command-line tool that counts the words in a text file.

## Scope and milestones
- M1 (count words) — I can run `bin/wc-lite <file>` and see its word count. [current]
- M2 (count many) — I can count several files at once. [planned]

## Components
| Component | Depth | Doc |
| --- | --- | --- |
| Counter_CLI | built | — |

## Decisions
- D1: shell script over `wc -w`. Kind `choice`, `settled`.
R
cat > Documentation/Roadmap-Word_Count.md <<'R'
# Roadmap: Word count

Design: Documentation/SystemDesign/Overview.md

## Milestones
- M1 (count words) — I can run `bin/wc-lite <file>` and see its word count. `owner`; touches: Counter_CLI [current]
  - Exit: `bin/wc-lite README.md` prints the file's word count; a missing file prints usage and exits 2.
- M2 (count many) — I can count several files at once. `proposed` [planned]

## Ladder (one line per rung, in order)
1. L1 — Can a script count the words of one file? [done]

## Rungs (detailed)

### L1: Count the words of one file
Question: Can a script count the words of one file?
Milestone: M1
Touches: Counter_CLI
Class: shape

## Horizon (not yet detailed)
- L2 — Can it count several files and print a total? (M2)

## Learning log
- L1 (done): `wc -w` is enough; usage error exits 2.
R
cat > Documentation/SystemDesign/Rung-L1-Count_Words.md <<'R'
# Rung L1: Count the words of one file
Status: folded back (2026-11-01)
Base: BASE_SHA

## Verification
- Regression test: `sh test.sh` "PASS count".

## Fold-back
- [x] Counter_CLI depth designed → built

## As built
- Counts with `wc -w`, strips padding with `tr`.
R
cat > Documentation/Completed/Tasklist-L1-Count_Words.md <<'R'
# Tasklist — L1 Count the words of one file

Source: Documentation/SystemDesign/Rung-L1-Count_Words.md

### G1 Count

- [x] T1 Write bin/wc-lite and test.sh
  - Model: standard (Sonnet 5.5)
  - Done when: `sh test.sh` passes.
R
printf 'A small tool that counts words.\n' > README.md
git init -q
g() { git -c user.name=Eval -c user.email=eval@example.invalid "$@"; }
g add CLAUDE.md README.md Documentation/SystemDesign/Overview.md
g commit -q -m "System design"
base=$(git rev-parse --short HEAD)
sed "s/BASE_SHA/$base/" Documentation/SystemDesign/Rung-L1-Count_Words.md > brief.tmp && mv brief.tmp Documentation/SystemDesign/Rung-L1-Count_Words.md
g add -A
g commit -q -m "Fold back rung L1"
