#!/usr/bin/env python3
"""Validate the distributable Swift design-pattern guidance."""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pattern_catalog import CONTENT_POLICY_URL, PATTERNS, Pattern, pattern_url


REQUIRED_HEADINGS = (
    "## Intent",
    "## Prefer Swift-native alternatives when",
    "## Choose this pattern when",
    "## Avoid it when",
    "## Design pressures",
    "## Swift implementation",
    "## Concurrency and ownership",
    "## Compare",
    "## Example",
    "## Review checklist",
    "## Attribution",
)

MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
FENCE_START = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})([^\r\n]*)")
BLOCKQUOTE_PREFIX = re.compile(r"^(?:[ \t]{0,3}>[ \t]?)+")
RAW_HTML_TOKEN = re.compile(
    (
        r"<!--|<\?|<!\[CDATA\[|<![A-Za-z]|"
        r"</?[A-Za-z][A-Za-z0-9-]*(?=[\s/>])"
    ),
    flags=re.IGNORECASE,
)
HTML_TAG_NAME = re.compile(r"</?([A-Za-z][A-Za-z0-9-]*)")
VOID_HTML_TAGS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)


@dataclass(frozen=True)
class MarkdownLink:
    target: str
    start: int


@dataclass(frozen=True)
class MarkdownScan:
    visible_text: str
    headings: frozenset[str]
    swift_examples: tuple[str, ...]
    links: tuple[MarkdownLink, ...]
    raw_html_lines: tuple[int, ...]


def extract_swift_examples(markdown: str) -> list[str]:
    """Return fenced Swift examples in source order."""

    return list(_scan_markdown(markdown).swift_examples)


def _mask_line(line: str) -> str:
    return "".join(character if character in "\r\n" else " " for character in line)


def _without_blockquote_prefix(line: str) -> str:
    prefix = BLOCKQUOTE_PREFIX.match(line)
    return line[prefix.end() :] if prefix else line


def _is_fence_close(
    line: str,
    fence_character: str,
    fence_length: int,
) -> bool:
    content = _without_blockquote_prefix(line)
    stripped = content.lstrip(" \t")
    if len(content) - len(stripped) > 3:
        return False
    marker = stripped.rstrip()
    return (
        len(marker) >= fence_length
        and set(marker) == {fence_character}
    )


def _mask_inline_code_line(
    line: str,
    open_marker: str | None,
) -> tuple[str, str | None]:
    masked = list(line)
    index = 0

    while index < len(line):
        if open_marker is not None:
            closing = line.find(open_marker, index)
            if closing == -1:
                return _mask_line(line), open_marker
            for position in range(index, closing + len(open_marker)):
                if masked[position] not in "\r\n":
                    masked[position] = " "
            index = closing + len(open_marker)
            open_marker = None
            continue

        if line[index] != "`":
            index += 1
            continue
        marker_end = index
        while marker_end < len(line) and line[marker_end] == "`":
            marker_end += 1
        marker = line[index:marker_end]
        closing = line.find(marker, marker_end)
        if closing == -1:
            for position in range(index, len(line)):
                if masked[position] not in "\r\n":
                    masked[position] = " "
            return "".join(masked), marker
        for position in range(index, closing + len(marker)):
            if masked[position] not in "\r\n":
                masked[position] = " "
        index = closing + len(marker)

    return "".join(masked), open_marker


def _mask_html_regions(
    line: str,
    comment_open: bool,
    raw_tag: str | None,
) -> tuple[str, bool, str | None]:
    masked = list(line)
    position = 0

    while position < len(line):
        if comment_open:
            closing = line.find("-->", position)
            end = len(line) if closing == -1 else closing + 3
            for index in range(position, end):
                if masked[index] not in "\r\n":
                    masked[index] = " "
            if closing == -1:
                return "".join(masked), True, raw_tag
            comment_open = False
            position = end
            continue

        if raw_tag is not None:
            if raw_tag == "?processing":
                closing_match = re.search(r"\?>", line[position:])
            elif raw_tag == "?cdata":
                closing_match = re.search(r"\]\]>", line[position:])
            elif raw_tag == "?declaration":
                closing_match = re.search(r">", line[position:])
            else:
                closing_match = re.search(
                    rf"</{re.escape(raw_tag)}\s*>",
                    line[position:],
                    flags=re.IGNORECASE,
                )
            end = (
                len(line)
                if closing_match is None
                else position + closing_match.end()
            )
            for index in range(position, end):
                if masked[index] not in "\r\n":
                    masked[index] = " "
            if closing_match is None:
                return "".join(masked), comment_open, raw_tag
            raw_tag = None
            position = end
            continue

        raw_match = RAW_HTML_TOKEN.search(line, position)
        if raw_match is None:
            break

        hidden_start = raw_match.start()
        token = raw_match.group()
        if token == "<!--":
            comment_open = True
        elif token == "<?":
            raw_tag = "?processing"
        elif token.casefold() == "<![cdata[":
            raw_tag = "?cdata"
        elif token.startswith("<!"):
            raw_tag = "?declaration"
        else:
            tag_match = HTML_TAG_NAME.match(line, hidden_start)
            tag_name = tag_match.group(1).casefold()
            tag_end = line.find(">", tag_match.end())
            if tag_end == -1:
                raw_tag = tag_name
            else:
                tag_end += 1
                tag_text = line[hidden_start:tag_end]
                is_closing = tag_text.startswith("</")
                is_self_closing = tag_text.rstrip().endswith("/>")
                for index in range(hidden_start, tag_end):
                    if masked[index] not in "\r\n":
                        masked[index] = " "
                position = tag_end
                if (
                    is_closing
                    or is_self_closing
                    or tag_name in VOID_HTML_TAGS
                ):
                    continue
                raw_tag = tag_name
        position = hidden_start

    return "".join(masked), comment_open, raw_tag


def _is_escaped(markdown: str, index: int) -> bool:
    backslash_count = 0
    index -= 1
    while index >= 0 and markdown[index] == "\\":
        backslash_count += 1
        index -= 1
    return backslash_count % 2 == 1


def _visible_markdown_links(markdown: str) -> list[MarkdownLink]:
    without_images = list(markdown)
    for image in MARKDOWN_IMAGE.finditer(markdown):
        if _is_escaped(markdown, image.start()):
            continue
        for index in range(image.start(), image.end()):
            if without_images[index] not in "\r\n":
                without_images[index] = " "

    markdown = "".join(without_images)
    links: list[MarkdownLink] = []
    for match in MARKDOWN_LINK.finditer(markdown):
        opening_bracket = match.start()
        if _is_escaped(markdown, opening_bracket):
            continue

        image_marker = opening_bracket - 1
        if (
            image_marker >= 0
            and markdown[image_marker] == "!"
            and not _is_escaped(markdown, image_marker)
        ):
            continue

        links.append(MarkdownLink(match.group(1), match.start()))
    return links


def _scan_markdown(markdown: str) -> MarkdownScan:
    visible_lines: list[str] = []
    swift_examples: list[str] = []
    fence_character: str | None = None
    fence_length = 0
    swift_fence = False
    swift_lines: list[str] = []
    inline_marker: str | None = None
    comment_open = False
    raw_tag: str | None = None
    raw_html_lines: list[int] = []

    for line_number, line in enumerate(
        markdown.splitlines(keepends=True),
        start=1,
    ):
        content = _without_blockquote_prefix(line)

        if fence_character is not None:
            if _is_fence_close(line, fence_character, fence_length):
                if swift_fence:
                    swift_examples.append(
                        "".join(swift_lines).rstrip() + "\n"
                    )
                fence_character = None
                fence_length = 0
                swift_fence = False
                swift_lines = []
            elif swift_fence:
                swift_lines.append(content)
            visible_lines.append(_mask_line(line))
            continue

        if not comment_open and raw_tag is None and inline_marker is None:
            fence_match = FENCE_START.match(content)
            if fence_match:
                marker = fence_match.group(1)
                fence_character = marker[0]
                fence_length = len(marker)
                swift_fence = fence_match.group(2).strip().casefold() == "swift"
                visible_lines.append(_mask_line(line))
                continue
            if content.startswith(("    ", "\t")):
                visible_lines.append(_mask_line(line))
                continue

        if comment_open or raw_tag is not None:
            visible_line, comment_open, raw_tag = _mask_html_regions(
                line,
                comment_open,
                raw_tag,
            )
        else:
            first_raw = RAW_HTML_TOKEN.search(line)
            first_tick = line.find("`")
            raw_precedes_inline = (
                first_raw is not None
                and (first_tick == -1 or first_raw.start() < first_tick)
            )
            if raw_precedes_inline:
                raw_html_lines.append(line_number)
                visible_line, comment_open, raw_tag = _mask_html_regions(
                    line,
                    comment_open,
                    raw_tag,
                )
            else:
                inline_masked, inline_marker = _mask_inline_code_line(
                    line,
                    inline_marker,
                )
                visible_raw = RAW_HTML_TOKEN.search(inline_masked)
                if visible_raw is not None:
                    raw_html_lines.append(line_number)
                visible_line, comment_open, raw_tag = _mask_html_regions(
                    inline_masked,
                    comment_open,
                    raw_tag,
                )
        visible_lines.append(visible_line)

    if fence_character is not None and swift_fence:
        swift_examples.append("".join(swift_lines).rstrip() + "\n")

    visible_text = "".join(visible_lines)
    headings = frozenset(visible_text.splitlines())
    return MarkdownScan(
        visible_text=visible_text,
        headings=headings,
        swift_examples=tuple(swift_examples),
        links=tuple(_visible_markdown_links(visible_text)),
        raw_html_lines=tuple(raw_html_lines),
    )


def _section_bounds(markdown: str, heading: str) -> tuple[int, int]:
    heading_start = markdown.find(f"{heading}\n")
    if heading_start == -1:
        return (0, 0)
    start = heading_start + len(heading) + 1
    next_heading = re.search(r"^## ", markdown[start:], flags=re.MULTILINE)
    end = len(markdown) if next_heading is None else start + next_heading.start()
    return (start, end)


def validate_reference(path: Path, pattern: Pattern) -> list[str]:
    """Validate one present pattern reference."""

    path = Path(path)
    markdown = path.read_text(encoding="utf-8")
    scan = _scan_markdown(markdown)
    errors = [
        f"{path.name}: raw HTML is not allowed on line {line_number}"
        for line_number in scan.raw_html_lines
    ]
    errors.extend(
        [
            f"{path.name}: missing heading '{heading}'"
            for heading in REQUIRED_HEADINGS
            if heading not in scan.headings
        ]
    )

    examples = scan.swift_examples
    if len(examples) != 1:
        errors.append(
            f"{path.name}: expected exactly one fenced Swift example; "
            f"found {len(examples)}"
        )

    attribution_start, attribution_end = _section_bounds(
        scan.visible_text,
        "## Attribution",
    )
    attribution_links = {
        link.target
        for link in scan.links
        if attribution_start <= link.start < attribution_end
    }
    source_url = pattern_url(pattern.slug)
    if source_url not in attribution_links:
        errors.append(
            f"{path.name}: attribution must link to {source_url}"
        )
    if CONTENT_POLICY_URL not in attribution_links:
        errors.append(
            f"{path.name}: attribution must link to {CONTENT_POLICY_URL}"
        )

    return errors


def validate_decision_index(path: Path) -> list[str]:
    """Require the decision index to link every canonical reference."""

    path = Path(path)
    if not path.is_file():
        return ["references/decision-index.md: missing decision index"]

    scan = _scan_markdown(path.read_text(encoding="utf-8"))
    errors = [
        f"{path.name}: raw HTML is not allowed on line {line_number}"
        for line_number in scan.raw_html_lines
    ]
    linked_targets = {
        link.target.split("#", maxsplit=1)[0].removeprefix("./")
        for link in scan.links
    }
    errors.extend(
        [
            (
                f"{path.name}: missing link "
                f"'{pattern.category}/{pattern.slug}.md' for {pattern.name}"
            )
            for pattern in PATTERNS
            if f"{pattern.category}/{pattern.slug}.md" not in linked_targets
        ]
    )
    return errors


def _compiler_diagnostic(stderr: str, temporary_path: Path) -> str:
    normalized = stderr.replace(str(temporary_path), "<example>")
    return " ".join(normalized.split())


def typecheck_swift_examples(paths: Iterable[Path]) -> list[str]:
    """Type-check every fenced Swift example in an isolated temporary file."""

    errors: list[str] = []
    for reference_path in sorted(map(Path, paths), key=lambda path: str(path)):
        markdown = reference_path.read_text(encoding="utf-8")
        for index, example in enumerate(extract_swift_examples(markdown), 1):
            with tempfile.TemporaryDirectory() as directory:
                example_path = Path(directory) / "example.swift"
                module_cache_path = Path(directory) / "module-cache"
                example_path.write_text(example, encoding="utf-8")
                try:
                    result = subprocess.run(
                        [
                            "xcrun",
                            "swiftc",
                            "-module-cache-path",
                            str(module_cache_path),
                            "-typecheck",
                            str(example_path),
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                except OSError as error:
                    errors.append(
                        f"{reference_path}: unable to run Swift compiler: "
                        f"{error}"
                    )
                    continue

                if result.returncode != 0:
                    diagnostic = _compiler_diagnostic(
                        result.stderr or result.stdout,
                        example_path,
                    )
                    errors.append(
                        f"{reference_path}: Swift example {index} failed "
                        f"to type-check: {diagnostic}"
                    )
    return errors


def validate_all(
    skill_root: Path,
    *,
    allow_incomplete: bool = False,
) -> list[str]:
    """Validate the canonical corpus rooted at ``skill_root``."""

    skill_root = Path(skill_root)
    errors: list[str] = []
    present_references: list[Path] = []

    for pattern in PATTERNS:
        relative_path = (
            Path("references") / pattern.category / f"{pattern.slug}.md"
        )
        reference_path = skill_root / relative_path
        if not reference_path.is_file():
            if not allow_incomplete:
                errors.append(
                    f"{relative_path.as_posix()}: missing pattern reference"
                )
            continue

        errors.extend(validate_reference(reference_path, pattern))
        present_references.append(reference_path)

    decision_index = skill_root / "references" / "decision-index.md"
    if decision_index.is_file() or not allow_incomplete:
        errors.extend(validate_decision_index(decision_index))

    errors.extend(typecheck_swift_examples(present_references))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Swift design-pattern reference content."
    )
    parser.add_argument("skill_root", type=Path)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="suppress missing corpus-file diagnostics during authorship",
    )
    arguments = parser.parse_args(argv)

    errors = validate_all(
        arguments.skill_root,
        allow_incomplete=arguments.allow_incomplete,
    )
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
