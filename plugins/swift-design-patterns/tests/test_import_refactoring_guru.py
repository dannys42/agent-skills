import importlib.util
import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path


PATTERN_CATALOG_MODULE_NAME = "choosing_swift_design_patterns.pattern_catalog"
PATTERN_CATALOG_PATH = (
    Path(__file__).parents[1]
    / "skills"
    / "choosing-swift-design-patterns"
    / "scripts"
    / "pattern_catalog.py"
)


def load_pattern_catalog():
    spec = importlib.util.spec_from_file_location(
        PATTERN_CATALOG_MODULE_NAME,
        PATTERN_CATALOG_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    previous_module = sys.modules.get(spec.name)
    had_previous_module = spec.name in sys.modules
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if had_previous_module:
            sys.modules[spec.name] = previous_module
        else:
            sys.modules.pop(spec.name, None)
    return module


class PatternCatalogTests(unittest.TestCase):
    def test_defines_canonical_twenty_two_pattern_catalog(self):
        self.assertTrue(
            PATTERN_CATALOG_PATH.is_file(),
            f"missing pattern catalog: {PATTERN_CATALOG_PATH}",
        )

        pattern_catalog = load_pattern_catalog()
        patterns = pattern_catalog.PATTERNS
        expected_patterns = (
            ("Abstract Factory", "abstract-factory", "creational"),
            ("Builder", "builder", "creational"),
            ("Factory Method", "factory-method", "creational"),
            ("Prototype", "prototype", "creational"),
            ("Singleton", "singleton", "creational"),
            ("Adapter", "adapter", "structural"),
            ("Bridge", "bridge", "structural"),
            ("Composite", "composite", "structural"),
            ("Decorator", "decorator", "structural"),
            ("Facade", "facade", "structural"),
            ("Flyweight", "flyweight", "structural"),
            ("Proxy", "proxy", "structural"),
            (
                "Chain of Responsibility",
                "chain-of-responsibility",
                "behavioral",
            ),
            ("Command", "command", "behavioral"),
            ("Iterator", "iterator", "behavioral"),
            ("Mediator", "mediator", "behavioral"),
            ("Memento", "memento", "behavioral"),
            ("Observer", "observer", "behavioral"),
            ("State", "state", "behavioral"),
            ("Strategy", "strategy", "behavioral"),
            ("Template Method", "template-method", "behavioral"),
            ("Visitor", "visitor", "behavioral"),
        )

        self.assertEqual(22, len(patterns))
        self.assertEqual(22, len({pattern.slug for pattern in patterns}))
        self.assertEqual(
            {"creational", "structural", "behavioral"},
            {pattern.category for pattern in patterns},
        )
        self.assertEqual(
            expected_patterns,
            tuple(
                (pattern.name, pattern.slug, pattern.category)
                for pattern in patterns
            ),
        )
        with self.assertRaises(FrozenInstanceError):
            patterns[0].name = "Mutable Factory"
        self.assertEqual(
            "https://refactoring.guru/design-patterns/abstract-factory/swift/example",
            pattern_catalog.pattern_url("abstract-factory"),
        )

    def test_loading_catalog_restores_synthetic_module_entry(self):
        missing_module = object()
        previous_module = sys.modules.pop(
            PATTERN_CATALOG_MODULE_NAME,
            missing_module,
        )
        existing_module = object()

        try:
            load_pattern_catalog()
            self.assertNotIn(PATTERN_CATALOG_MODULE_NAME, sys.modules)

            sys.modules[PATTERN_CATALOG_MODULE_NAME] = existing_module
            load_pattern_catalog()
            self.assertIs(
                existing_module,
                sys.modules[PATTERN_CATALOG_MODULE_NAME],
            )
        finally:
            if previous_module is missing_module:
                sys.modules.pop(PATTERN_CATALOG_MODULE_NAME, None)
            else:
                sys.modules[PATTERN_CATALOG_MODULE_NAME] = previous_module


if __name__ == "__main__":
    unittest.main()
