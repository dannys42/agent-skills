import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_PATH = (
    Path(__file__).parents[1]
    / "skills"
    / "choosing-swift-design-patterns"
    / "scripts"
)
PATTERN_CATALOG_PATH = SCRIPTS_PATH / "pattern_catalog.py"
VALIDATOR_PATH = SCRIPTS_PATH / "validate_content.py"
ORIGINALITY_AUDITOR_PATH = SCRIPTS_PATH / "audit_originality.py"

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


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


pattern_catalog = load_module("pattern_catalog", PATTERN_CATALOG_PATH)
sys.modules["pattern_catalog"] = pattern_catalog
try:
    validate_content = load_module("validate_content", VALIDATOR_PATH)
    audit_originality = load_module("audit_originality", ORIGINALITY_AUDITOR_PATH)
finally:
    sys.modules.pop("pattern_catalog", None)
Pattern = pattern_catalog.Pattern


def complete_reference(pattern):
    body = [f"# {pattern.name}"]
    for heading in REQUIRED_HEADINGS:
        body.extend(("", heading, "", f"Original guidance for {pattern.name}."))
        if heading == "## Example":
            body.extend(("", "```swift", "let value = 1", "```"))
        if heading == "## Attribution":
            body.extend(
                (
                    "",
                    (
                        f"[Refactoring.Guru: {pattern.name} in Swift]"
                        f"({pattern_catalog.pattern_url(pattern.slug)})."
                    ),
                    (
                        "[Refactoring.Guru Content Usage Policy]"
                        f"({pattern_catalog.CONTENT_POLICY_URL})."
                    ),
                    "No source code or illustrations are reproduced.",
                )
            )
    return "\n".join(body) + "\n"


class ContentValidatorTests(unittest.TestCase):
    def test_reports_missing_required_section(self):
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                "# State\n\n## Intent\n\nKeep state behavior focused.\n",
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(
                reference,
                Pattern("State", "state", "behavioral"),
            )

            self.assertIn(
                "state.md: missing heading '## Avoid it when'",
                errors,
            )

    def test_rejects_required_heading_hidden_in_html_comment(self):
        pattern = Pattern("State", "state", "behavioral")
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    "## Avoid it when",
                    "<!--\n## Avoid it when\n-->",
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                "state.md: missing heading '## Avoid it when'",
                errors,
            )

    def test_reports_missing_pattern_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_root = Path(directory)

            errors = validate_content.validate_all(skill_root)

            self.assertIn(
                "references/behavioral/state.md: missing pattern reference",
                errors,
            )

    def test_reports_missing_pattern_specific_attribution(self):
        pattern = Pattern("State", "state", "behavioral")
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    pattern_catalog.pattern_url(pattern.slug),
                    "https://refactoring.guru/design-patterns/swift",
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                (
                    "state.md: attribution must link to "
                    "https://refactoring.guru/design-patterns/state/swift/example"
                ),
                errors,
            )

    def test_rejects_plain_text_pattern_attribution_url(self):
        pattern = Pattern("State", "state", "behavioral")
        source_url = pattern_catalog.pattern_url(pattern.slug)
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    (
                        f"[Refactoring.Guru: {pattern.name} in Swift]"
                        f"({source_url})"
                    ),
                    source_url,
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                f"state.md: attribution must link to {source_url}",
                errors,
            )

    def test_rejects_pattern_attribution_link_hidden_in_html_comment(self):
        pattern = Pattern("State", "state", "behavioral")
        source_url = pattern_catalog.pattern_url(pattern.slug)
        visible_link = (
            f"[Refactoring.Guru: {pattern.name} in Swift]({source_url})"
        )
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    visible_link,
                    f"<!-- {visible_link} -->",
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                f"state.md: attribution must link to {source_url}",
                errors,
            )

    def test_rejects_pattern_attribution_link_hidden_in_fenced_code(self):
        pattern = Pattern("State", "state", "behavioral")
        source_url = pattern_catalog.pattern_url(pattern.slug)
        visible_link = (
            f"[Refactoring.Guru: {pattern.name} in Swift]({source_url})"
        )
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    visible_link,
                    f"```markdown\n{visible_link}\n```",
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                f"state.md: attribution must link to {source_url}",
                errors,
            )

    def test_rejects_pattern_attribution_link_hidden_in_inline_code(self):
        pattern = Pattern("State", "state", "behavioral")
        source_url = pattern_catalog.pattern_url(pattern.slug)
        visible_link = (
            f"[Refactoring.Guru: {pattern.name} in Swift]({source_url})"
        )
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    visible_link,
                    f"`{visible_link}`",
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                f"state.md: attribution must link to {source_url}",
                errors,
            )

    def test_rejects_pattern_attribution_link_hidden_in_indented_code(self):
        pattern = Pattern("State", "state", "behavioral")
        source_url = pattern_catalog.pattern_url(pattern.slug)
        visible_link = (
            f"[Refactoring.Guru: {pattern.name} in Swift]({source_url})"
        )
        for indentation in ("    ", "\t"):
            with self.subTest(indentation=repr(indentation)):
                with tempfile.TemporaryDirectory() as directory:
                    reference = Path(directory) / "state.md"
                    reference.write_text(
                        complete_reference(pattern).replace(
                            visible_link,
                            f"{indentation}{visible_link}",
                        ),
                        encoding="utf-8",
                    )

                    errors = validate_content.validate_reference(
                        reference,
                        pattern,
                    )

                self.assertIn(
                    f"state.md: attribution must link to {source_url}",
                    errors,
                )

    def test_rejects_escaped_pattern_attribution_pseudo_link(self):
        pattern = Pattern("State", "state", "behavioral")
        source_url = pattern_catalog.pattern_url(pattern.slug)
        visible_link = (
            f"[Refactoring.Guru: {pattern.name} in Swift]({source_url})"
        )
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    visible_link,
                    f"\\{visible_link}",
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                f"state.md: attribution must link to {source_url}",
                errors,
            )

    def test_rejects_pattern_attribution_image_destination(self):
        pattern = Pattern("State", "state", "behavioral")
        source_url = pattern_catalog.pattern_url(pattern.slug)
        visible_link = (
            f"[Refactoring.Guru: {pattern.name} in Swift]({source_url})"
        )
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    visible_link,
                    f"!{visible_link}",
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                f"state.md: attribution must link to {source_url}",
                errors,
            )

    def test_rejects_nested_image_source_as_pattern_attribution(self):
        pattern = Pattern("State", "state", "behavioral")
        source_url = pattern_catalog.pattern_url(pattern.slug)
        visible_link = (
            f"[Refactoring.Guru: {pattern.name} in Swift]({source_url})"
        )
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    visible_link,
                    (
                        f"[![Refactoring.Guru]({source_url})]"
                        "(https://example.com)"
                    ),
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                f"state.md: attribution must link to {source_url}",
                errors,
            )

    def test_rejects_pattern_link_in_blockquoted_fence(self):
        pattern = Pattern("State", "state", "behavioral")
        source_url = pattern_catalog.pattern_url(pattern.slug)
        visible_link = (
            f"[Refactoring.Guru: {pattern.name} in Swift]({source_url})"
        )
        for marker in ("```", "~~~"):
            with self.subTest(marker=marker):
                with tempfile.TemporaryDirectory() as directory:
                    reference = Path(directory) / "state.md"
                    reference.write_text(
                        complete_reference(pattern).replace(
                            visible_link,
                            (
                                f"> {marker}markdown\n"
                                f"> {visible_link}\n"
                                f"> {marker}"
                            ),
                        ),
                        encoding="utf-8",
                    )

                    errors = validate_content.validate_reference(
                        reference,
                        pattern,
                    )

                self.assertIn(
                    f"state.md: attribution must link to {source_url}",
                    errors,
                )

    def test_rejects_pattern_link_in_raw_html_text_block(self):
        pattern = Pattern("State", "state", "behavioral")
        source_url = pattern_catalog.pattern_url(pattern.slug)
        visible_link = (
            f"[Refactoring.Guru: {pattern.name} in Swift]({source_url})"
        )
        for tag in ("script", "style", "pre", "textarea"):
            with self.subTest(tag=tag):
                with tempfile.TemporaryDirectory() as directory:
                    reference = Path(directory) / "state.md"
                    reference.write_text(
                        complete_reference(pattern).replace(
                            visible_link,
                            f"<{tag}>\n{visible_link}\n</{tag}>",
                        ),
                        encoding="utf-8",
                    )

                    errors = validate_content.validate_reference(
                        reference,
                        pattern,
                    )

                self.assertIn(
                    f"state.md: attribution must link to {source_url}",
                    errors,
                )

    def test_rejects_div_containing_required_structure(self):
        pattern = Pattern("State", "state", "behavioral")
        source_url = pattern_catalog.pattern_url(pattern.slug)
        markdown = complete_reference(pattern)
        markdown = markdown.replace(
            "\n## Avoid it when\n\nOriginal guidance for State.\n",
            "\n",
        )
        markdown = markdown.replace(
            "```swift\nlet value = 1\n```\n",
            "",
        )
        markdown = markdown.replace(
            f"[Refactoring.Guru: {pattern.name} in Swift]({source_url}).\n",
            "",
        )
        markdown += (
            "<div>\n"
            "## Avoid it when\n"
            "```swift\n"
            "let hidden = true\n"
            "```\n"
            f"[Refactoring.Guru: State in Swift]({source_url}).\n"
            "</div>\n"
        )
        raw_line = markdown[: markdown.index("<div>")].count("\n") + 1
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(markdown, encoding="utf-8")

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                f"state.md: raw HTML is not allowed on line {raw_line}",
                errors,
            )
            self.assertIn(
                "state.md: missing heading '## Avoid it when'",
                errors,
            )
            self.assertIn(
                (
                    "state.md: expected exactly one fenced Swift example; "
                    "found 0"
                ),
                errors,
            )
            self.assertIn(
                f"state.md: attribution must link to {source_url}",
                errors,
            )

    def test_comment_backtick_does_not_hide_visible_attribution_or_example(self):
        pattern = Pattern("State", "state", "behavioral")
        markdown = "<!-- unmatched ` code span -->\n" + complete_reference(pattern)
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(markdown, encoding="utf-8")

            errors = validate_content.validate_reference(reference, pattern)

            self.assertEqual(
                ["state.md: raw HTML is not allowed on line 1"],
                errors,
            )

    def test_unmatched_html_comment_inside_swift_fence_is_ignored(self):
        pattern = Pattern("State", "state", "behavioral")
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    "let value = 1",
                    "let value = 1 // <!--",
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertEqual([], errors)

    def test_reports_reference_missing_from_decision_index(self):
        with tempfile.TemporaryDirectory() as directory:
            decision_index = Path(directory) / "decision-index.md"
            decision_index.write_text(
                "# Decision index\n\n"
                "[Strategy](behavioral/strategy.md)\n",
                encoding="utf-8",
            )

            errors = validate_content.validate_decision_index(decision_index)

            self.assertIn(
                (
                    "decision-index.md: missing link "
                    "'behavioral/state.md' for State"
                ),
                errors,
            )

    def test_rejects_decision_index_link_hidden_in_html_comment(self):
        with tempfile.TemporaryDirectory() as directory:
            decision_index = Path(directory) / "decision-index.md"
            decision_index.write_text(
                "# Decision index\n\n"
                "<!-- [State](behavioral/state.md) -->\n",
                encoding="utf-8",
            )

            errors = validate_content.validate_decision_index(decision_index)

            self.assertIn(
                (
                    "decision-index.md: missing link "
                    "'behavioral/state.md' for State"
                ),
                errors,
            )

    def test_rejects_decision_index_link_hidden_in_fenced_code(self):
        with tempfile.TemporaryDirectory() as directory:
            decision_index = Path(directory) / "decision-index.md"
            decision_index.write_text(
                "# Decision index\n\n"
                "```markdown\n[State](behavioral/state.md)\n```\n",
                encoding="utf-8",
            )

            errors = validate_content.validate_decision_index(decision_index)

            self.assertIn(
                (
                    "decision-index.md: missing link "
                    "'behavioral/state.md' for State"
                ),
                errors,
            )

    def test_rejects_decision_index_link_hidden_in_inline_code(self):
        with tempfile.TemporaryDirectory() as directory:
            decision_index = Path(directory) / "decision-index.md"
            decision_index.write_text(
                "# Decision index\n\n"
                "`[State](behavioral/state.md)`\n",
                encoding="utf-8",
            )

            errors = validate_content.validate_decision_index(decision_index)

            self.assertIn(
                (
                    "decision-index.md: missing link "
                    "'behavioral/state.md' for State"
                ),
                errors,
            )

    def test_rejects_decision_index_link_hidden_in_indented_code(self):
        for indentation in ("    ", "\t"):
            with self.subTest(indentation=repr(indentation)):
                with tempfile.TemporaryDirectory() as directory:
                    decision_index = Path(directory) / "decision-index.md"
                    decision_index.write_text(
                        "# Decision index\n\n"
                        f"{indentation}[State](behavioral/state.md)\n",
                        encoding="utf-8",
                    )

                    errors = validate_content.validate_decision_index(
                        decision_index
                    )

                self.assertIn(
                    (
                        "decision-index.md: missing link "
                        "'behavioral/state.md' for State"
                    ),
                    errors,
                )

    def test_rejects_escaped_decision_index_pseudo_link(self):
        with tempfile.TemporaryDirectory() as directory:
            decision_index = Path(directory) / "decision-index.md"
            decision_index.write_text(
                "# Decision index\n\n"
                "\\[State](behavioral/state.md)\n",
                encoding="utf-8",
            )

            errors = validate_content.validate_decision_index(decision_index)

            self.assertIn(
                (
                    "decision-index.md: missing link "
                    "'behavioral/state.md' for State"
                ),
                errors,
            )

    def test_rejects_decision_index_image_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            decision_index = Path(directory) / "decision-index.md"
            decision_index.write_text(
                "# Decision index\n\n"
                "![State](behavioral/state.md)\n",
                encoding="utf-8",
            )

            errors = validate_content.validate_decision_index(decision_index)

            self.assertIn(
                (
                    "decision-index.md: missing link "
                    "'behavioral/state.md' for State"
                ),
                errors,
            )

    def test_rejects_decision_index_link_in_blockquoted_fence(self):
        for marker in ("```", "~~~"):
            with self.subTest(marker=marker):
                with tempfile.TemporaryDirectory() as directory:
                    decision_index = Path(directory) / "decision-index.md"
                    decision_index.write_text(
                        "# Decision index\n\n"
                        f"> {marker}markdown\n"
                        "> [State](behavioral/state.md)\n"
                        f"> {marker}\n",
                        encoding="utf-8",
                    )

                    errors = validate_content.validate_decision_index(
                        decision_index
                    )

                self.assertIn(
                    (
                        "decision-index.md: missing link "
                        "'behavioral/state.md' for State"
                    ),
                    errors,
                )

    def test_rejects_decision_index_link_in_raw_html_text_block(self):
        for tag in ("script", "style", "pre", "textarea"):
            with self.subTest(tag=tag):
                with tempfile.TemporaryDirectory() as directory:
                    decision_index = Path(directory) / "decision-index.md"
                    decision_index.write_text(
                        "# Decision index\n\n"
                        f"<{tag}>\n"
                        "[State](behavioral/state.md)\n"
                        f"</{tag}>\n",
                        encoding="utf-8",
                    )

                    errors = validate_content.validate_decision_index(
                        decision_index
                    )

                self.assertIn(
                    (
                        "decision-index.md: missing link "
                        "'behavioral/state.md' for State"
                    ),
                    errors,
                )

    def test_rejects_processing_declaration_and_cdata_constructs(self):
        constructs = (
            "<?codex [State](behavioral/state.md) ?>",
            "<!NOTICE [State](behavioral/state.md)>",
            "<![CDATA[[State](behavioral/state.md)]]>",
        )
        for construct in constructs:
            with self.subTest(construct=construct):
                with tempfile.TemporaryDirectory() as directory:
                    decision_index = Path(directory) / "decision-index.md"
                    decision_index.write_text(
                        f"# Decision index\n\n{construct}\n",
                        encoding="utf-8",
                    )

                    errors = validate_content.validate_decision_index(
                        decision_index
                    )

                self.assertIn(
                    "decision-index.md: raw HTML is not allowed on line 3",
                    errors,
                )
                self.assertIn(
                    (
                        "decision-index.md: missing link "
                        "'behavioral/state.md' for State"
                    ),
                    errors,
                )

    def test_preserves_ordinary_link_and_visible_swift_fence(self):
        pattern = Pattern("State", "state", "behavioral")
        markdown = complete_reference(pattern)
        with tempfile.TemporaryDirectory() as directory:
            decision_index = Path(directory) / "decision-index.md"
            decision_index.write_text(
                "# Decision index\n\n"
                "[State](behavioral/state.md)\n",
                encoding="utf-8",
            )

            errors = validate_content.validate_decision_index(decision_index)

        self.assertNotIn(
            (
                "decision-index.md: missing link "
                "'behavioral/state.md' for State"
            ),
            errors,
        )
        self.assertEqual(
            ["let value = 1\n"],
            validate_content.extract_swift_examples(markdown),
        )

    def test_rejects_swift_example_hidden_in_html_comment(self):
        pattern = Pattern("State", "state", "behavioral")
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    "```swift\nlet value = 1\n```",
                    "<!--\n```swift\nlet value = 1\n```\n-->",
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                (
                    "state.md: expected exactly one fenced Swift example; "
                    "found 0"
                ),
                errors,
            )
            self.assertEqual(
                [],
                validate_content.extract_swift_examples(
                    reference.read_text(encoding="utf-8")
                ),
            )

    def test_requires_exactly_one_fenced_swift_example(self):
        pattern = Pattern("State", "state", "behavioral")
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern).replace(
                    "```swift\nlet value = 1\n```\n",
                    "",
                ),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertIn(
                (
                    "state.md: expected exactly one fenced Swift example; "
                    "found 0"
                ),
                errors,
            )

    def test_allow_incomplete_still_validates_present_reference(self):
        pattern = Pattern("State", "state", "behavioral")
        with tempfile.TemporaryDirectory() as directory:
            skill_root = Path(directory)
            reference = (
                skill_root
                / "references"
                / pattern.category
                / f"{pattern.slug}.md"
            )
            reference.parent.mkdir(parents=True)
            reference.write_text("# State\n", encoding="utf-8")

            errors = validate_content.validate_all(
                skill_root,
                allow_incomplete=True,
            )

            self.assertIn(
                "state.md: missing heading '## Intent'",
                errors,
            )
            self.assertNotIn(
                "references/creational/builder.md: missing pattern reference",
                errors,
            )
            self.assertNotIn(
                "references/decision-index.md: missing decision index",
                errors,
            )

    def test_allow_incomplete_still_validates_present_decision_index(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_root = Path(directory)
            decision_index = skill_root / "references" / "decision-index.md"
            decision_index.parent.mkdir(parents=True)
            decision_index.write_text("# Decision index\n", encoding="utf-8")

            errors = validate_content.validate_all(
                skill_root,
                allow_incomplete=True,
            )

            self.assertIn(
                (
                    "decision-index.md: missing link "
                    "'behavioral/state.md' for State"
                ),
                errors,
            )
            self.assertNotIn(
                "references/behavioral/state.md: missing pattern reference",
                errors,
            )

    def test_typecheck_uses_isolated_module_cache_and_example_paths(self):
        pattern = Pattern("State", "state", "behavioral")
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern),
                encoding="utf-8",
            )

            def complete_typecheck(command, **_):
                module_cache_path = Path(command[3])
                example_path = Path(command[5])
                self.assertEqual(
                    example_path.parent,
                    module_cache_path.parent,
                )
                self.assertTrue(example_path.is_file())
                self.assertTrue(module_cache_path.parent.is_dir())
                return mock.Mock(returncode=0, stderr="", stdout="")

            with mock.patch.object(
                validate_content.subprocess,
                "run",
                side_effect=complete_typecheck,
            ) as run:
                errors = validate_content.typecheck_swift_examples([reference])

            self.assertEqual([], errors)
            run.assert_called_once()
            command = run.call_args.args[0]
            self.assertEqual(
                ["xcrun", "swiftc", "-module-cache-path"],
                command[:3],
            )
            module_cache_path = Path(command[3])
            self.assertEqual("-typecheck", command[4])
            example_path = Path(command[5])
            self.assertEqual(example_path.parent, module_cache_path.parent)
            self.assertEqual(
                {
                    "check": False,
                    "capture_output": True,
                    "text": True,
                },
                run.call_args.kwargs,
            )

    def test_typecheck_reports_compiler_launch_failure_deterministically(self):
        pattern = Pattern("State", "state", "behavioral")
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern),
                encoding="utf-8",
            )

            with mock.patch.object(
                validate_content.subprocess,
                "run",
                side_effect=OSError("tool unavailable"),
            ):
                errors = validate_content.typecheck_swift_examples([reference])

            self.assertEqual(
                [
                    (
                        f"{reference}: unable to run Swift compiler: "
                        "tool unavailable"
                    )
                ],
                errors,
            )

    def test_accepts_complete_reference(self):
        pattern = Pattern("State", "state", "behavioral")
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                complete_reference(pattern),
                encoding="utf-8",
            )

            errors = validate_content.validate_reference(reference, pattern)

            self.assertEqual([], errors)

    def test_originality_audit_reports_twenty_word_exact_match(self):
        matching_words = (
            "alpha bravo charlie delta echo foxtrot golf hotel india juliet "
            "kilo lima mike november oscar papa quebec romeo sierra tango"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            research_root = root / "research"
            skill_root = root / "skill"
            source = research_root / "state.html"
            distributable = skill_root / "references" / "behavioral" / "state.md"
            source.parent.mkdir(parents=True)
            distributable.parent.mkdir(parents=True)
            source.write_text(
                f"<html><body><p>{matching_words}</p></body></html>",
                encoding="utf-8",
            )
            distributable.write_text(
                f"# State\n\n{matching_words}\n",
                encoding="utf-8",
            )

            errors = audit_originality.audit_originality(
                research_root,
                skill_root,
            )

            self.assertEqual(
                [
                    (
                        f"{distributable}: exact 20-word match with {source}: "
                        f"{matching_words}"
                    )
                ],
                errors,
            )

    def test_originality_audit_reports_missing_input_corpora(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            research_root = root / "research"
            skill_root = root / "skill"
            research_root.mkdir()
            skill_root.mkdir()

            errors = audit_originality.audit_originality(
                research_root,
                skill_root,
            )

            self.assertEqual(
                [
                    f"{research_root}: no research HTML files found",
                    f"{skill_root}: no distributable Markdown files found",
                ],
                errors,
            )

    def test_originality_audit_reports_each_missing_input_independently(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            research_root = root / "research"
            skill_root = root / "skill"
            research_root.mkdir()
            skill_root.mkdir()
            source = research_root / "state.html"
            distributable = skill_root / "state.md"

            source.write_text("<p>Research text.</p>", encoding="utf-8")
            errors = audit_originality.audit_originality(
                research_root,
                skill_root,
            )
            self.assertEqual(
                [f"{skill_root}: no distributable Markdown files found"],
                errors,
            )

            source.unlink()
            distributable.write_text("Original guidance.", encoding="utf-8")
            errors = audit_originality.audit_originality(
                research_root,
                skill_root,
            )
            self.assertEqual(
                [f"{research_root}: no research HTML files found"],
                errors,
            )


if __name__ == "__main__":
    unittest.main()
