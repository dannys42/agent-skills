import hashlib
import json
import re
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).parents[1]
REPOSITORY_ROOT = PLUGIN_ROOT.parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "crafting-compelling-stories"
PLUGIN_NAME = "storytelling"
SKILL_NAME = "crafting-compelling-stories"
SKILL_DESCRIPTION = (
    "Use when creating, reshaping, or critiquing stories, narrative writing, "
    "marketing or conversion copy, founder, product, customer, or brand "
    "stories, case studies, speeches, talks, scripts, narrative-driven "
    "educational explanations, fiction, hooks, story openings, narrative "
    "arcs, tension, concrete imagery, or endings; not for grammar-only "
    "correction, literal transcription, code, or ordinary factual prose "
    "without narrative intent"
)
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = (
    "Audience-aware storytelling and narrative copy grounded in an attributed "
    "Joanna Wiebe framework"
)
PLUGIN_KEYWORDS = [
    "storytelling",
    "copywriting",
    "marketing",
    "narrative",
    "speeches",
    "fiction",
    "agent-skills",
]
REPOSITORY_DESCRIPTION = (
    "Portable agent skills for Swift and Apple-platform development, "
    "agent-skill engineering, storytelling, and writing."
)
SOURCE_URL = "https://www.youtube.com/watch?v=oCnxnaVg0bY"
STORYTELLING_TABLE_ROW = (
    "| `storytelling` | `crafting-compelling-stories` | Audience-aware "
    "storytelling and narrative copy grounded in an attributed Joanna Wiebe "
    "framework |"
)
TRANSCRIPT_LICENSE_NOTICE = (
    "License notice: This archival transcript is not covered by the "
    "repository GPL-3.0-or-later license; redistribution rights are not established."
)
TRANSCRIPT_PROVENANCE_PREFIX = """Reference only — not runtime skill instructions.
Presenter and synthesizer of this eight-principle presentation: Joanna Wiebe
Video: The Psychology of Storytelling That Will Change Your Life
Source: https://www.youtube.com/watch?v=oCnxnaVg0bY
Purpose: Archival provenance for the distilled, independently worded skill.
License notice: This archival transcript is not covered by the repository GPL-3.0-or-later license; redistribution rights are not established.

"""
# No pre-move hash was captured. This digest freezes the mechanically moved
# current body; it does not claim independent proof of pre-move equivalence.
TRANSCRIPT_BODY_SHA256 = (
    "c9081c720b18d2be55a8654336aa72778aa3a0aafb01f7f0a43ee2646d6022ba"
)
UNSUPPORTED_EFFECTIVENESS_CLAIM_PATTERN = re.compile(
    r"(?:"
    r"\b\d+(?:\.\d+)?\s*%|"
    r"\b(?:twice|\d+(?:\.\d+)?(?:x|\s+times?))\s+"
    r"(?:as\s+|more\s+)?"
    r"(?:effective|memorable|engaging|persuasive|successful)\b"
    r")",
    flags=re.IGNORECASE,
)
REQUIRED_CASE_IDS = {
    "saas-landing-page",
    "founder-story",
    "speech-opening",
    "fiction-scene",
    "incomplete-marketing-brief",
    "preserve-voice-edit",
    "grammar-only-negative-trigger",
    "factual-prose-negative-trigger",
}
REQUIRED_CASE_PROMPTS = {
    "saas-landing-page": (
        "Write the narrative opening and CTA for a landing page for Briefly, "
        "a meeting-summary tool. Audience: engineering managers. Supplied "
        "facts only: it turns an uploaded transcript into a summary; Acme's "
        "pilot reduced its weekly recap-writing time from 90 minutes to 25 "
        "minutes; Acme approved use of its name. Do not add product "
        "capabilities or results."
    ),
    "founder-story": (
        "Turn these notes into a 250-word founder story: Mina ran a "
        "neighborhood bakery; a freezer failed at 4:40 a.m. before a wedding "
        "order; handwritten inventory made it hard to see what could be "
        "remade; she later built a simple batch tracker with her brother. Do "
        "not invent quotations, dates, customers, or outcomes."
    ),
    "speech-opening": (
        "Write a 90-second opening for a talk to first-time managers about "
        "giving useful feedback. Desired feeling: recognized, then hopeful. "
        "Avoid sales language."
    ),
    "fiction-scene": (
        "Rewrite this slow opening as a vivid 180-word scene while preserving "
        "third-person limited voice and the fact that Mara is avoiding a "
        "letter: 'Mara was nervous. The room was old and unpleasant. There "
        "was a letter on the table that she did not want to read.'"
    ),
    "incomplete-marketing-brief": (
        "Write launch copy for a new meal-planning app. I have not supplied "
        "its features, audience research, testimonials, price, results, or "
        "launch date. Make it persuasive and urgent."
    ),
    "preserve-voice-edit": (
        "Tighten this copy without changing its dry, understated voice: 'At "
        "2:13 on Tuesday, the dashboard went red. This was inconvenient. We "
        "had, after all, promised the board that red dashboards were now "
        "mostly a historical artifact. The office ficus remained neutral. "
        "Our incident log did not.' Remove details that do not earn a place, "
        "but preserve any detail that establishes tone or pays off."
    ),
    "grammar-only-negative-trigger": (
        "Correct grammar only: 'The reports is ready and it were sent "
        "yesterday.' Do not introduce narrative or marketing language."
    ),
    "factual-prose-negative-trigger": (
        "Summarize these facts in two plain sentences without storytelling: "
        "Water freezes at 0°C at standard atmospheric pressure. Dissolved "
        "solutes can lower the freezing point."
    ),
}
REQUIRED_RUBRIC = [
    "appropriate_triggering",
    "audience_goal_medium_constraints_handled",
    "structure_adapted_to_task",
    "principles_applied_selectively",
    "orientation_imagery_details_payoff_ending_effective",
    "supplied_voice_and_facts_preserved",
    "unsupported_claims_not_invented",
    "ethical_marketing_and_proportionate_cta",
    "deliverable_first_without_framework_lecture",
]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def extract_markdown_section(markdown, heading, following_heading_pattern):
    match = re.search(
        rf"(?ms)^{re.escape(heading)}\n(?P<body>.*?)(?=^{following_heading_pattern}|\Z)",
        markdown,
    )
    if match is None:
        raise ValueError(f"missing Markdown section {heading}")
    return match.group("body")


def normalize_shell_command(command):
    return re.sub(r"\\\s*\n\s*", "", command).strip()


def normalize_whitespace(value):
    return " ".join(value.split())


def parse_skill_frontmatter(skill):
    frontmatter = re.match(
        r"\A---\n"
        r"(?P<name_key>[^:\n]+):(?P<name>[^\n]*)\n"
        r"(?P<description_key>[^:\n]+):(?P<description>[^\n]*)\n"
        r"(?:(?P<license_key>[^:\n]+):(?P<license>[^\n]*)\n)?"
        r"---(?:\n|\Z)",
        skill,
    )
    if frontmatter is None or (
        frontmatter.group("name_key"),
        frontmatter.group("description_key"),
    ) != ("name", "description"):
        raise ValueError("frontmatter must begin with name and description")

    result = {
        "name": parse_frontmatter_string(frontmatter.group("name"), "name"),
        "description": parse_frontmatter_string(
            frontmatter.group("description"),
            "description",
        ),
    }
    if frontmatter.group("license_key") is not None:
        if frontmatter.group("license_key") != "license":
            raise ValueError("frontmatter license key must be license")
        result["license"] = parse_frontmatter_string(
            frontmatter.group("license"),
            "license",
        )
    return result


def parse_frontmatter_string(raw_value, key):
    value = raw_value.strip()
    error = f"frontmatter {key} must be a string"
    if not value:
        raise ValueError(error)

    if value.startswith('"'):
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError as exception:
            raise ValueError(error) from exception
        if not isinstance(parsed_value, str):
            raise ValueError(error)
        return parsed_value

    if value.startswith("'"):
        if re.fullmatch(r"'(?:[^']|'')*'", value) is None:
            raise ValueError(error)
        return value[1:-1].replace("''", "'")

    non_string_scalar = re.fullmatch(
        r"(?:"
        r"[\[{].*|"
        r"[|>][+-]?[0-9]?|"
        r"~|null|true|false|yes|no|on|off|"
        r"[-+]?(?:"
        r"0[bB][01_]+|0[oO][0-7_]+|0[xX][0-9a-fA-F_]+|"
        r"[0-9][0-9_]*|"
        r"(?:[0-9][0-9_]*)?\.[0-9_]+(?:[eE][-+]?[0-9_]+)?|"
        r"[0-9][0-9_]*(?:\.[0-9_]*)?[eE][-+]?[0-9_]+|"
        r"\.(?:inf|nan)"
        r")"
        r")",
        value,
        flags=re.IGNORECASE,
    )
    if non_string_scalar is not None:
        raise ValueError(error)
    return value


class PluginContractTests(unittest.TestCase):
    def test_repository_descriptions_share_canonical_scope(self):
        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
        readme_intro = extract_markdown_section(
            readme,
            "# Danny Sung's Agent Skills",
            r"## ",
        )
        self.assertEqual(
            REPOSITORY_DESCRIPTION,
            normalize_whitespace(readme_intro),
        )

        claude_marketplace = load_json(
            REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json"
        )
        self.assertEqual(
            {
                "description": REPOSITORY_DESCRIPTION,
                "version": "1.0.0",
            },
            claude_marketplace["metadata"],
        )

        cursor_marketplace = load_json(
            REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json"
        )
        self.assertEqual(
            {"description": REPOSITORY_DESCRIPTION},
            cursor_marketplace["metadata"],
        )

    def test_repository_marketplaces_expose_plugin_once(self):
        marketplace_paths = (
            REPOSITORY_ROOT / ".agents" / "plugins" / "marketplace.json",
            REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json",
            REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json",
        )
        for path in marketplace_paths:
            with self.subTest(path=path):
                marketplace = load_json(path)
                matches = [
                    plugin
                    for plugin in marketplace["plugins"]
                    if plugin["name"] == PLUGIN_NAME
                ]
                self.assertEqual(1, len(matches))

    def test_codex_marketplace_uses_canonical_plugin_entry(self):
        marketplace = load_json(
            REPOSITORY_ROOT / ".agents" / "plugins" / "marketplace.json"
        )
        entry = next(
            plugin
            for plugin in marketplace["plugins"]
            if plugin["name"] == PLUGIN_NAME
        )
        self.assertEqual(
            {
                "name": PLUGIN_NAME,
                "source": {
                    "source": "local",
                    "path": "./plugins/storytelling",
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Writing",
            },
            entry,
        )

    def test_claude_marketplace_uses_canonical_plugin_entry(self):
        marketplace = load_json(
            REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json"
        )
        entry = next(
            plugin
            for plugin in marketplace["plugins"]
            if plugin["name"] == PLUGIN_NAME
        )
        self.assertEqual(
            {
                "name": PLUGIN_NAME,
                "source": "./plugins/storytelling",
                "version": PLUGIN_VERSION,
                "description": PLUGIN_DESCRIPTION,
                "category": "writing",
                "keywords": PLUGIN_KEYWORDS,
                "tags": ["storytelling", "copywriting", "narrative"],
            },
            entry,
        )

    def test_cursor_marketplace_uses_canonical_plugin_entry(self):
        marketplace = load_json(
            REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json"
        )
        entry = next(
            plugin
            for plugin in marketplace["plugins"]
            if plugin["name"] == PLUGIN_NAME
        )
        self.assertEqual(
            {
                "name": PLUGIN_NAME,
                "source": "plugins/storytelling",
                "description": PLUGIN_DESCRIPTION,
            },
            entry,
        )

    def test_cursor_marketplace_uses_supported_entry_fields(self):
        marketplace = load_json(
            REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json"
        )
        supported_fields = {
            "name",
            "source",
            "description",
            "minClientVersions",
        }
        for plugin in marketplace["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                self.assertLessEqual(set(plugin), supported_fields)

    def test_repository_readme_exposes_plugin_and_installation(self):
        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
        overview_heading = "### `crafting-compelling-stories`"
        install_heading = "## Install `crafting-compelling-stories`"
        self.assertEqual(1, readme.count(STORYTELLING_TABLE_ROW))
        self.assertEqual(1, readme.count(overview_heading))
        self.assertEqual(1, readme.count(install_heading))

        plugins_section = extract_markdown_section(
            readme,
            "## Plugins",
            r"## ",
        )
        overview = extract_markdown_section(
            readme,
            overview_heading,
            r"### ",
        )
        install = extract_markdown_section(
            readme,
            install_heading,
            r"## ",
        )
        marketplace_inventory = extract_markdown_section(
            readme,
            "## Marketplace adapters and open registries",
            r"## ",
        )
        license_section = extract_markdown_section(
            readme,
            "## License",
            r"## ",
        )

        self.assertIn(STORYTELLING_TABLE_ROW, plugins_section)
        normalized_overview = normalize_whitespace(overview)
        for required_text in (
            "stories, marketing and conversion copy, speeches, talks, "
            "scripts, and fiction",
            "selectively synthesizes",
            "without fabricating facts, outcomes, quotations, or evidence",
            "Joanna Wiebe",
            SOURCE_URL,
            "transcript is provenance, not runtime instructions",
            "not independently validated science",
            "third-party redistribution caveat",
            "[THIRD_PARTY_NOTICES.md](plugins/storytelling/THIRD_PARTY_NOTICES.md)",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, normalized_overview)

        command_blocks = re.findall(r"```bash\n(.*?)\n```", install, re.DOTALL)
        normalized_commands = [
            normalize_shell_command(command) for command in command_blocks
        ]
        command_lines = [
            line
            for command in normalized_commands
            for line in command.splitlines()
        ]
        self.assertIn(
            "claude plugin install storytelling@danny-sung-agent-skills",
            command_lines,
        )
        self.assertIn(
            "codex plugin add storytelling@danny-sung-agent-skills",
            command_lines,
        )
        self.assertIn(
            "npx skills add dannys42/agent-skills --skill "
            "crafting-compelling-stories --global --agent <agent>",
            normalized_commands,
        )
        gemini_inventory_match = re.search(
            r"(?ms)^- Gemini extension metadata:\n(?P<body>.*?)(?=^- )",
            marketplace_inventory,
        )
        self.assertIsNotNone(gemini_inventory_match)
        gemini_inventory = gemini_inventory_match.group("body")
        self.assertEqual(1, gemini_inventory.count("and"))
        self.assertIn(
            "`plugins/skill-development-optimizer/gemini-extension.json`, "
            "and `plugins/storytelling/gemini-extension.json`",
            normalize_whitespace(gemini_inventory),
        )
        self.assertEqual(
            [
                "plugins/swift-testing/gemini-extension.json",
                "plugins/swift-design-patterns/gemini-extension.json",
                "plugins/swift-code-organization/gemini-extension.json",
                "plugins/skill-development-optimizer/gemini-extension.json",
                "plugins/storytelling/gemini-extension.json",
            ],
            re.findall(
                r"`(plugins/[^`]+/gemini-extension\.json)`",
                gemini_inventory,
            ),
        )
        normalized_license = normalize_whitespace(license_section)
        self.assertIn(
            "The repository license does not cover the archival transcript",
            normalized_license,
        )
        self.assertIn(
            "redistribution rights are not established",
            normalized_license,
        )

    def test_portable_manifests_share_exact_canonical_identity(self):
        canonical_identity = {
            "name": PLUGIN_NAME,
            "version": PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
        }
        for relative_path in (
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            ".cursor-plugin/plugin.json",
            "gemini-extension.json",
        ):
            with self.subTest(path=relative_path):
                manifest = load_json(PLUGIN_ROOT / relative_path)
                self.assertEqual(canonical_identity, {
                    key: manifest[key] for key in canonical_identity
                })

    def test_openai_agent_metadata_is_exact(self):
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            """interface:
  display_name: "Crafting Compelling Stories"
  short_description: "Shape vivid stories and narrative copy"
  default_prompt: "Use $crafting-compelling-stories to shape this material into an audience-aware story."
""",
            metadata,
        )

    def test_skill_frontmatter_declares_gpl_license(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = parse_skill_frontmatter(skill)
        self.assertEqual(SKILL_NAME, frontmatter["name"])
        self.assertEqual(SKILL_DESCRIPTION, frontmatter["description"])
        self.assertEqual("GPL-3.0-or-later", frontmatter["license"])

    def test_frontmatter_parser_accepts_plain_and_quoted_strings(self):
        for description in (
            "Shape audience-aware stories",
            '"Shape audience-aware stories"',
            "'Shape audience-aware stories'",
        ):
            with self.subTest(description=description):
                skill = (
                    "---\n"
                    "name: crafting-compelling-stories\n"
                    f"description: {description}\n"
                    "---\n"
                )
                self.assertEqual(
                    "Shape audience-aware stories",
                    parse_skill_frontmatter(skill)["description"],
                )

    def test_frontmatter_parser_rejects_non_string_yaml_scalars(self):
        for description in (
            "[storytelling]",
            "{purpose: storytelling}",
            "null",
            "true",
            "42",
            "3.14",
        ):
            with self.subTest(description=description):
                skill = (
                    "---\n"
                    "name: crafting-compelling-stories\n"
                    f"description: {description}\n"
                    "---\n"
                )
                with self.assertRaisesRegex(
                    ValueError,
                    "frontmatter description must be a string",
                ):
                    parse_skill_frontmatter(skill)

    def test_evaluation_corpus_matches_exact_cases(self):
        cases = load_json(PLUGIN_ROOT / "tests" / "evaluation-cases.json")
        self.assertEqual(8, len(cases))
        for case in cases:
            with self.subTest(case=case):
                self.assertIsInstance(case, dict)
                self.assertEqual({"id", "prompt"}, set(case))
                self.assertIsInstance(case["id"], str)
                self.assertTrue(case["id"].strip())
                self.assertIsInstance(case["prompt"], str)
                self.assertTrue(case["prompt"].strip())

        identifiers = [case["id"] for case in cases]
        self.assertEqual(REQUIRED_CASE_IDS, set(identifiers))
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(
            REQUIRED_CASE_PROMPTS,
            {case["id"]: case["prompt"] for case in cases},
        )

    def test_evaluation_rubric_matches_exact_ordered_keys(self):
        rubric = load_json(PLUGIN_ROOT / "tests" / "evaluation-rubric.json")
        self.assertEqual(REQUIRED_RUBRIC, rubric)

    def test_archival_transcript_is_relocated_with_attribution(self):
        transcript = (
            SKILL_ROOT / "references" / "joanna-wiebe-storytelling-transcript.txt"
        ).read_text(encoding="utf-8")
        self.assertTrue(
            transcript.startswith(TRANSCRIPT_PROVENANCE_PREFIX),
            "transcript must start with the exact provenance prefix",
        )
        transcript_body = transcript[len(TRANSCRIPT_PROVENANCE_PREFIX):]
        self.assertEqual(
            TRANSCRIPT_BODY_SHA256,
            hashlib.sha256(transcript_body.encode("utf-8")).hexdigest(),
            "archival transcript body changed",
        )
        header = transcript.split("\n\n", 1)[0]
        for required_text in (
            "Joanna Wiebe",
            "The Psychology of Storytelling That Will Change Your Life",
            SOURCE_URL,
            "Reference only",
            TRANSCRIPT_LICENSE_NOTICE,
        ):
            self.assertIn(required_text, header)
        self.assertFalse(
            (
                REPOSITORY_ROOT
                / "misc"
                / "psychology_storytelling_transcript.txt"
            ).exists()
        )

    def test_third_party_notice_discloses_transcript_rights(self):
        notice = (PLUGIN_ROOT / "THIRD_PARTY_NOTICES.md").read_text(
            encoding="utf-8"
        )
        for required_text in (
            "The Psychology of Storytelling That Will Change Your Life",
            SOURCE_URL,
            "Presenter and synthesizer of this eight-principle presentation: "
            "Joanna Wiebe",
            TRANSCRIPT_LICENSE_NOTICE,
            "Verify rights before public redistribution",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, notice)

        readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("THIRD_PARTY_NOTICES.md", readme)

    def test_skill_contains_required_operating_guardrails(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "Do not read the archival transcript during ordinary use",
            "Never invent",
            "Choose one primary structure",
            "Apply only the principles that serve the assignment",
            "Preserve the author's voice",
            "Return the deliverable first",
            "Define the obstacle concretely without dehumanizing people or "
            "manufacturing fear",
            "Do not vilify protected or identifiable groups",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_skill_guards_incomplete_marketing_briefs(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "as claims—not harmless scene-setting",
            "do not draft those elements as known",
            "clearly labeled message skeleton",
            "materially affect truthful completion",
            "not a mandatory checklist",
            "visibly marked as a placeholder",
            "without evidence",
            "prioritize truthful completion",
            "missing-facts request as the deliverable",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_skill_does_not_make_unsupported_effectiveness_claims(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for unsupported_claim in ("40%", "70%", "twice as memorable"):
            with self.subTest(unsupported_claim=unsupported_claim):
                self.assertNotIn(unsupported_claim, skill)

    def test_effectiveness_claim_guard_catches_common_numeric_claims(self):
        for unsupported_claim in (
            "40% more memorable",
            "70 % more effective",
            "twice as memorable",
            "2x more effective",
            "3 times as engaging",
        ):
            with self.subTest(unsupported_claim=unsupported_claim):
                self.assertIsNotNone(
                    UNSUPPORTED_EFFECTIVENESS_CLAIM_PATTERN.search(
                        unsupported_claim
                    )
                )

    def test_skill_body_has_no_numeric_effectiveness_claims(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        skill_body = skill.split("---\n", 2)[2]
        self.assertIsNone(
            UNSUPPORTED_EFFECTIVENESS_CLAIM_PATTERN.search(skill_body),
            "skill body must not contain numeric effectiveness claims",
        )


if __name__ == "__main__":
    unittest.main()
