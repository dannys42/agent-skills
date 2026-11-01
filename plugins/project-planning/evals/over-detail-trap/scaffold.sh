#!/bin/sh
# Fixture: a fully synthetic project. The vision doc invites deep design of the
# matching and evaluation machinery; a good first pass keeps it to the first milestone.
set -eu
mkdir -p Documentation
cat > Documentation/Vision.md <<'EOF'
# Bookmark Sorter

A macOS app that suggests which of my existing bookmark folders a new bookmark belongs in.

I have about 2,000 Safari bookmarks in about 120 folders, nested up to four levels.
New bookmarks pile up in an "Unsorted" folder and I never file them.

## What I want eventually

- Suggest the right folder for each unsorted bookmark, with a confidence and a reason.
- Apply a suggestion in one click, with undo.
- Learn from my corrections.
- Later: Chrome and Firefox bookmarks, dead-link detection, duplicates, and
  proposing new folders when nothing fits.

## Ideas for how matching could work

- Domain match: bookmarks from the same site usually live together.
- Title keywords, weighted by how distinctive each word is across folders.
- Page text: fetch the page and compare text embeddings with each folder's pages.
- An on-device language model to rerank the top few folders.
- A cloud model, opt-in, for the hard cases.
- Combine the methods into one score, calibrate a confidence threshold, and only
  auto-file above it.

## Measuring it

My existing folders are the ground truth: hide a bookmark, predict its folder,
compare. I want to know how good each method is, alone and combined, before I
trust any of them. Per-method reports, threshold sweeps, confusion between
sibling folders and timing would all be useful.

## Principles

- Learn from my folders; no built-in categories.
- Never confidently wrong: asking is better than misfiling.
- Private: page text stays on the Mac unless I opt in to a cloud model.
EOF
git init -q
git -c user.name=Eval -c user.email=eval@example.invalid add -A
git -c user.name=Eval -c user.email=eval@example.invalid commit -q -m "Vision"
