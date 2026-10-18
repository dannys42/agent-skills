#!/bin/sh
# Tag HEAD with a version and push main and the tag to both remotes.
#   scripts/release.sh <version>      e.g. scripts/release.sh 0.10.2
# Aborts before pushing anything if the version is missing, the tag already exists locally or on
# a remote, a remote is unreachable, HEAD is not main, or tracked files have uncommitted changes.
# git push sometimes exits non-zero with "failed to push some refs" after the refs were updated, so
# the result is checked against the remotes (ls-remote), not the push exit code.
set -eu

remotes="origin sungheroes"
branch=main

die() { echo "abort: $*" >&2; exit 1; }

# --- Arguments and repository ---------------------------------------------------------------
[ $# -eq 1 ] && [ -n "$1" ] || { echo "usage: $0 <version>" >&2; exit 2; }
version=$1
cd "$(git rev-parse --show-toplevel)"

# --- Local checks: right branch, clean tree, usable tag name, tag not taken ------------------
[ "$(git symbolic-ref --short HEAD)" = "$branch" ] || die "not on $branch"
git diff --quiet HEAD -- || die "tracked files have uncommitted changes"
git check-ref-format "refs/tags/$version" || die "'$version' is not a valid tag name"
! git rev-parse -q --verify "refs/tags/$version" >/dev/null || die "tag $version already exists locally"

# --- Remote checks: every remote reachable and without this tag ------------------------------
for r in $remotes; do
  existing=$(git ls-remote --tags "$r" "refs/tags/$version") || die "cannot reach $r"
  [ -z "$existing" ] || die "tag $version already exists on $r"
done

# --- Tag HEAD --------------------------------------------------------------------------------
git tag "$version" || die "git tag failed"
head=$(git rev-parse HEAD)

# --- Push to each remote and verify against what the remote reports --------------------------
status=0
for r in $remotes; do
  git push "$r" "$branch" "$version" || true   # exit code is unreliable, verified below
  remote_main=$(git ls-remote "$r" "refs/heads/$branch" | cut -f1)
  remote_tag=$(git ls-remote "$r" "refs/tags/$version" | cut -f1)
  if [ "$remote_main" = "$head" ] && [ "$remote_tag" = "$head" ]; then
    echo "ok: $r has $branch and $version at $head"
  else
    echo "FAILED: $r does not have $branch and $version at $head" >&2
    status=1
  fi
done
exit $status
