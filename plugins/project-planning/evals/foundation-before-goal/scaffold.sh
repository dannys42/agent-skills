#!/bin/sh
# Fixture: a fully synthetic project. The goal is an experiment loop; what it
# stands on is data collection, part of which cannot be backfilled.
set -eu
mkdir -p Documentation
cat > Documentation/Goal.md <<'EOF'
# Shop Lab

A tool for a one-person online shop (handmade ceramics, about 60 products) to
test changes to product pages and read the results honestly.

## The goal

Run a change as an experiment: write a hypothesis, change one thing on a
product page (price, main photo, title, description), and after enough time,
read whether it helped, with the confounds named. Keep a durable record of every
change and what was learned, so nothing is a "mystery edit".

## Where the data is

- Shop platform orders API: every order since the shop opened, three years ago.
- Shop platform storefront analytics API: daily sessions, product page views
  and add-to-carts per product. Kept for 90 days only; older days are gone.
- Shop platform product API: the current product pages. No history of changes;
  the platform does not keep old versions.
- Ad platform reports: daily spend and clicks, last 13 months.
- Newsletter tool: send dates and links clicked, full history.

## Volume

About 25 orders a day across all products; the best seller gets about 300 page
views a week.

## Later

Automated experiments within limits I set, a schedule of tests, and
recommendations of what to test next. A web dashboard someday.
EOF
git init -q
git -c user.name=Eval -c user.email=eval@example.invalid add -A
git -c user.name=Eval -c user.email=eval@example.invalid commit -q -m "Goal"
