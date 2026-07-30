#!/usr/bin/env python3
"""Find exact 20-word overlaps between research and distributable guidance."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


SHINGLE_SIZE = 20
URL = re.compile(r"https?://[^\s)>]+", flags=re.IGNORECASE)
WORD = re.compile(r"[^\W_]+(?:[’'-][^\W_]+)*", flags=re.UNICODE)


class VisibleHTMLText(HTMLParser):
    """Collect visible HTML text while excluding headings and metadata."""

    IGNORED_TAGS = {
        "head",
        "script",
        "style",
        "noscript",
        "svg",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.casefold() in self.IGNORED_TAGS:
            self.ignored_depth += 1

    def handle_endtag(self, tag):
        if tag.casefold() in self.IGNORED_TAGS and self.ignored_depth:
            self.ignored_depth -= 1

    def handle_data(self, data):
        if not self.ignored_depth:
            self.parts.append(data)


def _html_text(raw_html: str) -> str:
    parser = VisibleHTMLText()
    parser.feed(raw_html)
    parser.close()
    return " ".join(parser.parts)


def _markdown_text(markdown: str) -> str:
    return "\n".join(
        line
        for line in markdown.splitlines()
        if not line.lstrip().startswith("#")
    )


def _words(text: str) -> tuple[str, ...]:
    without_urls = URL.sub(" ", text)
    return tuple(match.group().casefold() for match in WORD.finditer(without_urls))


def _shingles(words: tuple[str, ...]) -> Iterable[tuple[str, ...]]:
    for start in range(len(words) - SHINGLE_SIZE + 1):
        yield words[start : start + SHINGLE_SIZE]


def audit_originality(
    research_root: Path,
    skill_root: Path,
) -> list[str]:
    """Report every distinct exact shingle shared by source and distribution."""

    research_root = Path(research_root)
    skill_root = Path(skill_root)
    source_paths = sorted(research_root.rglob("*.html"))
    distributable_paths = sorted(skill_root.rglob("*.md"))
    errors = []
    if not source_paths:
        errors.append(f"{research_root}: no research HTML files found")
    if not distributable_paths:
        errors.append(
            f"{skill_root}: no distributable Markdown files found"
        )
    if errors:
        return errors

    source_shingles: dict[tuple[str, ...], set[Path]] = defaultdict(set)

    for source_path in source_paths:
        source_words = _words(
            _html_text(source_path.read_text(encoding="utf-8", errors="replace"))
        )
        for shingle in _shingles(source_words):
            source_shingles[shingle].add(source_path)

    matches: set[tuple[Path, Path, tuple[str, ...]]] = set()
    for distributable_path in distributable_paths:
        distributable_words = _words(
            _markdown_text(
                distributable_path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            )
        )
        for shingle in _shingles(distributable_words):
            for source_path in source_shingles.get(shingle, ()):
                matches.add((distributable_path, source_path, shingle))

    return [
        (
            f"{distributable}: exact {SHINGLE_SIZE}-word match with {source}: "
            f"{' '.join(shingle)}"
        )
        for distributable, source, shingle in sorted(
            matches,
            key=lambda match: (
                str(match[0]),
                str(match[1]),
                match[2],
            ),
        )
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit distributable Markdown for exact research overlap."
    )
    parser.add_argument("research_root", type=Path)
    parser.add_argument("skill_root", type=Path)
    arguments = parser.parse_args(argv)

    errors = audit_originality(
        arguments.research_root,
        arguments.skill_root,
    )
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
