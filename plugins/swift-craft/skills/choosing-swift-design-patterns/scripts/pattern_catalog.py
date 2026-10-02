from dataclasses import dataclass


@dataclass(frozen=True)
class Pattern:
    name: str
    slug: str
    category: str


CATALOG_URL = "https://refactoring.guru/design-patterns/swift"
CONTENT_POLICY_URL = "https://refactoring.guru/content-usage-policy"

PATTERNS = (
    Pattern("Abstract Factory", "abstract-factory", "creational"),
    Pattern("Builder", "builder", "creational"),
    Pattern("Factory Method", "factory-method", "creational"),
    Pattern("Prototype", "prototype", "creational"),
    Pattern("Singleton", "singleton", "creational"),
    Pattern("Adapter", "adapter", "structural"),
    Pattern("Bridge", "bridge", "structural"),
    Pattern("Composite", "composite", "structural"),
    Pattern("Decorator", "decorator", "structural"),
    Pattern("Facade", "facade", "structural"),
    Pattern("Flyweight", "flyweight", "structural"),
    Pattern("Proxy", "proxy", "structural"),
    Pattern("Chain of Responsibility", "chain-of-responsibility", "behavioral"),
    Pattern("Command", "command", "behavioral"),
    Pattern("Iterator", "iterator", "behavioral"),
    Pattern("Mediator", "mediator", "behavioral"),
    Pattern("Memento", "memento", "behavioral"),
    Pattern("Observer", "observer", "behavioral"),
    Pattern("State", "state", "behavioral"),
    Pattern("Strategy", "strategy", "behavioral"),
    Pattern("Template Method", "template-method", "behavioral"),
    Pattern("Visitor", "visitor", "behavioral"),
)


def pattern_url(slug: str) -> str:
    return f"https://refactoring.guru/design-patterns/{slug}/swift/example"
