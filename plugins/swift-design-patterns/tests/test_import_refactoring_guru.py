import importlib.util
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import threading
import time
import unittest
from dataclasses import FrozenInstanceError
from email.message import Message
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPSHandler, Request, build_opener
from urllib.response import addinfourl
from unittest import mock


PATTERN_CATALOG_MODULE_NAME = "choosing_swift_design_patterns.pattern_catalog"
PATTERN_CATALOG_PATH = (
    Path(__file__).parents[1]
    / "skills"
    / "choosing-swift-design-patterns"
    / "scripts"
    / "pattern_catalog.py"
)
IMPORTER_MODULE_NAME = "choosing_swift_design_patterns.import_refactoring_guru"
IMPORTER_PATH = PATTERN_CATALOG_PATH.with_name("import_refactoring_guru.py")


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


def load_importer():
    catalog = load_pattern_catalog()
    spec = importlib.util.spec_from_file_location(
        IMPORTER_MODULE_NAME,
        IMPORTER_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    previous_catalog = sys.modules.get("pattern_catalog")
    previous_importer = sys.modules.get(spec.name)
    had_catalog = "pattern_catalog" in sys.modules
    had_importer = spec.name in sys.modules
    sys.modules["pattern_catalog"] = catalog
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if had_catalog:
            sys.modules["pattern_catalog"] = previous_catalog
        else:
            sys.modules.pop("pattern_catalog", None)
        if had_importer:
            sys.modules[spec.name] = previous_importer
        else:
            sys.modules.pop(spec.name, None)
    return module


class FakeClock:
    def __init__(self):
        self.value = 100.0
        self.sleeps = []

    def monotonic(self):
        return self.value

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.value += seconds


class ByteResponse(io.BytesIO):
    def __init__(self, content=b"ok", status=200, final_url=None):
        super().__init__(content)
        self.status = status
        self.final_url = final_url

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def geturl(self):
        return self.final_url


class RecordingOpener:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []
        self.timeouts = []

    def open(self, request, timeout=None):
        self.requests.append(request)
        self.timeouts.append(timeout)
        if not self.outcomes:
            raise AssertionError("unexpected request")
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def http_error(status, retry_after=None):
    headers = {}
    if retry_after is not None:
        headers["Retry-After"] = str(retry_after)
    return HTTPError(
        "https://example.test/resource",
        status,
        f"HTTP {status}",
        headers,
        io.BytesIO(b"error"),
    )


def canonical_catalog_html(extra_links=""):
    catalog = load_pattern_catalog()
    links = "".join(
        f'<a href="/design-patterns/{pattern.slug}/swift/example">'
        f"{pattern.name}</a>"
        for pattern in catalog.PATTERNS
    )
    return f"<html><body>{links}{extra_links}</body></html>".encode()


def write_cached_page(output, slug, content=b"cached", source_url=None):
    importer = load_importer()
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{slug}.html").write_bytes(content)
    return {
        "source_url": source_url or f"https://example.test/{slug}",
        "fetched_at": "2026-01-01T00:00:00+00:00",
        "http_status": 200,
        "byte_count": len(content),
        "sha256": importer.sha256_bytes(content),
    }


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


class ImportClientTests(unittest.TestCase):
    def test_rejects_interval_shorter_than_five_seconds(self):
        importer = load_importer()

        with self.assertRaisesRegex(ValueError, "at least 5"):
            importer.ImportClient(min_interval=4.999)

    def test_rejects_nonfinite_interval(self):
        importer = load_importer()

        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "finite"):
                    importer.ImportClient(min_interval=value)

    def test_rejects_invalid_retry_counts(self):
        importer = load_importer()

        for value in (-1, 1.5, True):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "retries"):
                    importer.ImportClient(retries=value)

    def test_validates_timeout_and_passes_it_to_opener(self):
        importer = load_importer()
        for value in (0, -1, float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "timeout"):
                    importer.ImportClient(timeout=value)
        opener = RecordingOpener([ByteResponse()])

        importer.ImportClient(opener=opener, timeout=12.5).fetch(
            "https://example.test"
        )

        self.assertEqual([12.5], opener.timeouts)

    def test_waits_exactly_five_seconds_between_attempts(self):
        importer = load_importer()
        clock = FakeClock()
        opener = RecordingOpener([ByteResponse(b"first"), ByteResponse(b"second")])
        client = importer.ImportClient(
            opener=opener,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )

        client.fetch("https://example.test/first")
        client.fetch("https://example.test/second")

        self.assertEqual([5.0], clock.sleeps)
        self.assertEqual(105.0, clock.value)

    def test_waits_full_interval_after_previous_response_completes(self):
        importer = load_importer()
        clock = FakeClock()

        class SlowResponse(ByteResponse):
            def read(self, *arguments):
                content = super().read(*arguments)
                clock.value += 2.0
                return content

        attempts = []
        client = importer.ImportClient(
            opener=RecordingOpener([SlowResponse(), ByteResponse()]),
            monotonic=clock.monotonic,
            sleep=clock.sleep,
            attempt_logger=attempts.append,
        )

        client.fetch("https://example.test/first")
        client.fetch("https://example.test/second")

        self.assertEqual([5.0], clock.sleeps)
        self.assertEqual(7.0, attempts[1]["monotonic"] - attempts[0]["monotonic"])

    def test_waits_full_interval_after_unexpected_response_failure(self):
        importer = load_importer()
        clock = FakeClock()

        class FailingResponse(ByteResponse):
            def read(self, *arguments):
                clock.value += 2.0
                raise TimeoutError("read timed out unexpectedly")

        attempts = []
        client = importer.ImportClient(
            opener=RecordingOpener([FailingResponse(), ByteResponse()]),
            monotonic=clock.monotonic,
            sleep=clock.sleep,
            attempt_logger=attempts.append,
        )

        with self.assertRaises(TimeoutError):
            client.fetch("https://example.test/first")
        client.fetch("https://example.test/second")

        self.assertEqual([5.0], clock.sleeps)
        self.assertEqual(7.0, attempts[1]["monotonic"] - attempts[0]["monotonic"])

    def test_short_retry_after_never_shortens_minimum_interval(self):
        importer = load_importer()
        clock = FakeClock()
        opener = RecordingOpener(
            [http_error(429, retry_after=2), ByteResponse()]
        )
        client = importer.ImportClient(
            opener=opener,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )

        client.fetch("https://example.test")

        self.assertEqual([10.0], clock.sleeps)

    def test_long_retry_after_on_server_error_extends_interval(self):
        importer = load_importer()
        clock = FakeClock()
        opener = RecordingOpener(
            [http_error(503, retry_after=20), ByteResponse()]
        )
        client = importer.ImportClient(
            opener=opener,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )

        client.fetch("https://example.test")

        self.assertEqual([20.0], clock.sleeps)

    def test_retries_only_retryable_failures_with_bounded_attempts(self):
        importer = load_importer()
        retryable_failures = (
            http_error(429),
            http_error(503),
            URLError("offline"),
        )
        for failure in retryable_failures:
            with self.subTest(failure=repr(failure)):
                clock = FakeClock()
                opener = RecordingOpener([failure, failure, failure])
                client = importer.ImportClient(
                    retries=2,
                    opener=opener,
                    monotonic=clock.monotonic,
                    sleep=clock.sleep,
                )
                with self.assertRaises(type(failure)) as raised:
                    client.fetch("https://example.test")
                if isinstance(raised.exception, HTTPError):
                    raised.exception.close()
                self.assertEqual(3, len(opener.requests))
                self.assertEqual([10.0, 20.0], clock.sleeps)

    def test_nonretryable_client_error_is_raised_immediately(self):
        importer = load_importer()
        opener = RecordingOpener([http_error(404)])
        client = importer.ImportClient(opener=opener)

        with self.assertRaises(HTTPError) as raised:
            client.fetch("https://example.test/missing")

        self.assertEqual(1, len(opener.requests))
        self.assertTrue(raised.exception.fp.closed)

    def test_closes_exhausted_retryable_http_error_before_raising(self):
        importer = load_importer()
        clock = FakeClock()
        failures = [http_error(503), http_error(503), http_error(503)]
        client = importer.ImportClient(
            opener=RecordingOpener(failures),
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )

        with self.assertRaises(HTTPError):
            client.fetch("https://example.test")

        self.assertTrue(all(failure.fp.closed for failure in failures))

    def test_closes_retryable_http_error_body_before_retrying(self):
        importer = load_importer()
        clock = FakeClock()
        failure = http_error(500)
        opener = RecordingOpener([failure, ByteResponse()])
        client = importer.ImportClient(
            opener=opener,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )

        client.fetch("https://example.test")

        self.assertTrue(failure.fp.closed)

    def test_sets_descriptive_user_agent_and_logs_every_attempt(self):
        importer = load_importer()
        clock = FakeClock()
        attempts = []
        opener = RecordingOpener([http_error(500), ByteResponse()])
        client = importer.ImportClient(
            opener=opener,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
            attempt_logger=attempts.append,
        )

        client.fetch("https://example.test/page")

        self.assertEqual(
            importer.DEFAULT_USER_AGENT,
            opener.requests[0].get_header("User-agent"),
        )
        self.assertEqual([1, 2], [entry["attempt"] for entry in attempts])
        self.assertEqual(
            ["https://example.test/page"] * 2,
            [entry["url"] for entry in attempts],
        )

    def test_ignores_invalid_retry_after_values(self):
        importer = load_importer()
        for value in ("-1", "nan", "inf", "not-a-number"):
            with self.subTest(value=value):
                clock = FakeClock()
                client = importer.ImportClient(
                    opener=RecordingOpener(
                        [http_error(503, retry_after=value), ByteResponse()]
                    ),
                    monotonic=clock.monotonic,
                    sleep=clock.sleep,
                )

                client.fetch("https://example.test")

                self.assertEqual([10.0], clock.sleeps)

    def test_records_requested_and_final_response_urls(self):
        importer = load_importer()
        client = importer.ImportClient(
            opener=RecordingOpener(
                [ByteResponse(final_url="https://refactoring.guru/final")]
            )
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            manifest = {"patterns": {}}

            metadata = importer.import_pattern(
                "state",
                output,
                client,
                "https://refactoring.guru/design-patterns/state/swift/example",
                manifest,
            )

        self.assertEqual(
            "https://refactoring.guru/design-patterns/state/swift/example",
            metadata["requested_url"],
        )
        self.assertEqual(
            "https://refactoring.guru/final",
            metadata["final_url"],
        )


class CatalogDiscoveryTests(unittest.TestCase):
    def test_normalizes_fragment_links_and_ignores_origin_lookalikes(self):
        importer = load_importer()
        catalog = load_pattern_catalog()
        links = []
        for pattern in catalog.PATTERNS:
            relative_url = (
                f"/design-patterns/{pattern.slug}/swift/example"
            )
            links.extend(
                (
                    f'<a href="{relative_url}#example-0">First</a>',
                    f'<a href="https://refactoring.guru'
                    f'{relative_url}#example-1">Second</a>',
                    f'<a href="{relative_url}#lang-features">Features</a>',
                )
            )
        links.extend(
            (
                '<a href="https://evil.test/design-patterns/state/swift/'
                'example#example-0">Cross origin</a>',
                '<a href="http://refactoring.guru/design-patterns/state/'
                'swift/example#example-0">Downgrade</a>',
                '<a href="https://[invalid/ignored">Malformed</a>',
            )
        )

        discovered = importer.discover_pattern_urls(
            "".join(links).encode()
        )

        self.assertEqual(
            {
                pattern.slug: catalog.pattern_url(pattern.slug)
                for pattern in catalog.PATTERNS
            },
            discovered,
        )

    def test_discovers_only_swift_example_links_and_requires_all_patterns(self):
        importer = load_importer()
        html = canonical_catalog_html(
            '<a href="/design-patterns/state/java/example">Java</a>'
            '<a href="https://other.test/design-patterns/state/swift/example">'
            "Other host</a>"
            '<a href="/design-patterns/UPPER/swift/example">Upper</a>'
        )

        discovered = importer.discover_pattern_urls(html)

        self.assertEqual(22, len(discovered))
        self.assertEqual(
            "https://refactoring.guru/design-patterns/state/swift/example",
            discovered["state"],
        )

    def test_missing_or_extra_canonical_slug_fails_clearly(self):
        importer = load_importer()
        missing = canonical_catalog_html().replace(
            b'<a href="/design-patterns/state/swift/example">State</a>',
            b"",
        )
        with self.assertRaisesRegex(ValueError, "missing.*state"):
            importer.discover_pattern_urls(missing)

        extra = canonical_catalog_html(
            '<a href="/design-patterns/not-canonical/swift/example">Extra</a>'
        )
        with self.assertRaisesRegex(ValueError, "extra.*not-canonical"):
            importer.discover_pattern_urls(extra)


class CacheAndImportTests(unittest.TestCase):
    def test_retained_root_descriptor_anchors_reads_logs_and_atomic_writes(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            selected_root = temporary_path / "cache"
            selected_root.mkdir()
            selected_root.joinpath("catalog.html").write_bytes(b"inside")
            outside = temporary_path / "outside"
            outside.mkdir()

            with importer.CacheRoot.open(selected_root) as cache:
                moved_root = temporary_path / "moved-cache"
                selected_root.rename(moved_root)
                selected_root.symlink_to(outside, target_is_directory=True)

                self.assertEqual(
                    b"inside",
                    cache.read_bytes("catalog.html"),
                )
                cache.atomic_write("manifest.json", b"inside manifest")
                importer._request_log_writer(cache)(
                    {"url": "https://refactoring.guru/"}
                )

            self.assertEqual(b"inside manifest", (moved_root / "manifest.json").read_bytes())
            self.assertTrue((moved_root / "requests.jsonl").is_file())
            self.assertEqual([], list(outside.iterdir()))

    def test_hardlinked_request_log_is_rejected_without_mutating_outside_file(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            output = temporary_path / "cache"
            output.mkdir()
            outside = temporary_path / "outside.log"
            outside.write_bytes(b"preserve\n")
            os.link(outside, output / "requests.jsonl")
            client = importer.ImportClient(opener=RecordingOpener([]))

            with self.assertRaisesRegex(
                importer.ImportFailure,
                "requests.jsonl.*hard link",
            ):
                importer.run_import(output, client=client)

            self.assertEqual(b"preserve\n", outside.read_bytes())
            self.assertEqual([], client.opener.requests)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation is unavailable")
    def test_fifo_cache_target_is_rejected_without_blocking(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "cache"
            output.mkdir()
            os.mkfifo(output / "requests.jsonl")
            client = importer.ImportClient(opener=RecordingOpener([]))

            with self.assertRaisesRegex(
                importer.ImportFailure,
                "requests.jsonl.*regular file",
            ):
                importer.run_import(output, client=client)

            self.assertEqual([], client.opener.requests)

    def test_disappearing_read_target_is_a_path_specific_import_failure(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            target = output / "catalog.html"
            target.write_bytes(b"catalog")

            with importer.CacheRoot.open(output) as cache:
                real_validate = cache.validate
                validation_count = 0

                def unlink_after_validation(filename):
                    nonlocal validation_count
                    file_status = real_validate(filename)
                    validation_count += 1
                    if validation_count == 1:
                        target.unlink(missing_ok=True)
                    return file_status

                with mock.patch.object(
                    cache,
                    "validate",
                    side_effect=unlink_after_validation,
                ):
                    with self.assertRaisesRegex(
                        importer.ImportFailure,
                        "catalog.html.*disappeared",
                    ):
                        cache.read_bytes("catalog.html", allow_missing=True)

    def test_disappearing_root_during_atomic_write_fails_path_specifically(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "cache"
            output.mkdir()

            with importer.CacheRoot.open(output) as cache:
                output.rmdir()
                with self.assertRaisesRegex(
                    importer.ImportFailure,
                    re.escape(str(output / "manifest.json")),
                ):
                    cache.atomic_write("manifest.json", b"manifest")

    def test_closed_cache_root_never_falls_back_to_current_working_directory(self):
        importer = load_importer()
        operations = (
            (
                "read",
                lambda cache: cache.read_bytes("catalog.html"),
            ),
            (
                "atomic-write",
                lambda cache: cache.atomic_write(
                    "manifest.json",
                    b"cache manifest",
                ),
            ),
            (
                "request-log",
                lambda cache: importer._request_log_writer(cache)(
                    {"url": "https://refactoring.guru/"}
                ),
            ),
        )

        for close_mode in ("explicit", "context-exit"):
            for operation_name, operation in operations:
                with self.subTest(
                    close_mode=close_mode,
                    operation=operation_name,
                ):
                    with tempfile.TemporaryDirectory() as temporary:
                        temporary_path = Path(temporary)
                        output = temporary_path / "cache"
                        output.mkdir()
                        working_directory = temporary_path / "cwd"
                        working_directory.mkdir()
                        working_directory.joinpath("catalog.html").write_bytes(
                            b"cwd catalog"
                        )
                        working_directory.joinpath("manifest.json").write_bytes(
                            b"cwd manifest"
                        )
                        working_directory.joinpath("requests.jsonl").write_bytes(
                            b"cwd log\n"
                        )
                        original_contents = {
                            path.name: path.read_bytes()
                            for path in working_directory.iterdir()
                        }

                        if close_mode == "explicit":
                            cache = importer.CacheRoot.open(output)
                            cache.close()
                            cache.close()
                        else:
                            with importer.CacheRoot.open(output) as cache:
                                pass

                        previous_directory = Path.cwd()
                        try:
                            os.chdir(working_directory)
                            with self.assertRaisesRegex(
                                importer.ImportFailure,
                                re.escape(str(output)),
                            ):
                                operation(cache)
                        finally:
                            os.chdir(previous_directory)

                        self.assertEqual(
                            original_contents,
                            {
                                path.name: path.read_bytes()
                                for path in working_directory.iterdir()
                            },
                        )
                        self.assertEqual([], list(output.iterdir()))

    def test_atomic_write_fails_closed_when_dir_fd_open_is_unavailable(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            real_open = importer.os.open

            def reject_dir_fd(path, flags, *args, **kwargs):
                if "dir_fd" in kwargs:
                    raise TypeError("dir_fd is unavailable")
                return real_open(path, flags, *args, **kwargs)

            with importer.CacheRoot.open(output) as cache:
                with mock.patch.object(
                    importer.os,
                    "open",
                    side_effect=reject_dir_fd,
                ):
                    with self.assertRaisesRegex(
                        importer.ImportFailure,
                        "directory-relative.*manifest.json",
                    ):
                        cache.atomic_write("manifest.json", b"manifest")

            self.assertEqual([], list(output.iterdir()))

    def test_rejects_symlinked_managed_cache_artifacts_before_io(self):
        importer = load_importer()
        catalog = canonical_catalog_html()
        managed_artifacts = (
            ("manifest.json", b'{"catalog": {}, "patterns": {}}'),
            ("catalog.html", catalog),
            ("state.html", b"cached state"),
            ("requests.jsonl", b"existing log\n"),
        )

        for artifact_name, outside_content in managed_artifacts:
            with self.subTest(artifact_name=artifact_name):
                with tempfile.TemporaryDirectory() as temporary:
                    temporary_path = Path(temporary)
                    output = temporary_path / "cache"
                    output.mkdir()
                    outside = temporary_path / f"outside-{artifact_name}"
                    outside.write_bytes(outside_content)
                    (output / artifact_name).symlink_to(outside)
                    opener = RecordingOpener([])
                    client = importer.ImportClient(opener=opener)

                    with self.assertRaisesRegex(
                        importer.ImportFailure,
                        re.escape(str(output / artifact_name)),
                    ):
                        importer.run_import(output, client=client)

                    self.assertEqual([], opener.requests)
                    self.assertEqual(outside_content, outside.read_bytes())
                    self.assertTrue((output / artifact_name).is_symlink())

    def test_rejects_non_regular_managed_cache_artifacts_before_io(self):
        importer = load_importer()
        for artifact_name in (
            "manifest.json",
            "catalog.html",
            "state.html",
            "requests.jsonl",
        ):
            with self.subTest(artifact_name=artifact_name):
                with tempfile.TemporaryDirectory() as temporary:
                    output = Path(temporary) / "cache"
                    output.mkdir()
                    (output / artifact_name).mkdir()
                    opener = RecordingOpener([])
                    client = importer.ImportClient(opener=opener)

                    with self.assertRaisesRegex(
                        importer.ImportFailure,
                        re.escape(str(output / artifact_name)),
                    ):
                        importer.run_import(output, client=client)

                    self.assertEqual([], opener.requests)
                    self.assertTrue((output / artifact_name).is_dir())

    def test_accepts_a_symlink_as_the_selected_output_root(self):
        importer = load_importer()
        catalog = canonical_catalog_html()
        responses = [ByteResponse(catalog)] + [
            ByteResponse(pattern.slug.encode())
            for pattern in load_pattern_catalog().PATTERNS
        ]
        clock = FakeClock()
        client = importer.ImportClient(
            opener=RecordingOpener(responses),
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )

        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            real_output = temporary_path / "real-cache"
            real_output.mkdir()
            selected_output = temporary_path / "selected-cache"
            selected_output.symlink_to(real_output, target_is_directory=True)

            manifest = importer.run_import(selected_output, client=client)

            self.assertEqual(22, len(manifest["patterns"]))
            self.assertTrue(selected_output.is_symlink())
            self.assertTrue((real_output / "manifest.json").is_file())

    def test_cache_validation_rejects_traversal_before_reading_outside(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "cache"
            output.mkdir()
            outside = output.parent / "outside.html"
            outside.write_bytes(b"outside")
            manifest = {
                "patterns": {
                    "../outside": {
                        "sha256": importer.sha256_bytes(b"outside"),
                    }
                }
            }

            with self.assertRaisesRegex(ValueError, "canonical slug"):
                importer.cached_page_is_valid(
                    output,
                    "../outside",
                    manifest,
                )

    def test_page_cache_permission_error_raises_without_refetch(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            metadata = write_cached_page(
                output,
                "state",
                source_url=load_pattern_catalog().pattern_url("state"),
            )
            manifest = {"patterns": {"state": metadata}}
            opener = RecordingOpener([])
            client = importer.ImportClient(opener=opener)

            with mock.patch.object(
                importer.CacheRoot,
                "read_bytes",
                autospec=True,
                side_effect=PermissionError("denied"),
            ):
                with self.assertRaisesRegex(
                    importer.ImportFailure,
                    "state.html.*denied",
                ):
                    importer.import_pattern(
                        "state",
                        output,
                        client,
                        load_pattern_catalog().pattern_url("state"),
                        manifest,
                    )

            self.assertEqual([], opener.requests)
            self.assertEqual(b"cached", (output / "state.html").read_bytes())

    def test_catalog_cache_permission_error_raises_without_refetch(self):
        importer = load_importer()
        catalog = canonical_catalog_html()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            (output / "catalog.html").write_bytes(catalog)
            manifest = {
                "catalog": {"sha256": importer.sha256_bytes(catalog)},
                "patterns": {},
            }
            (output / "manifest.json").write_text(json.dumps(manifest))
            opener = RecordingOpener([])
            client = importer.ImportClient(opener=opener)

            original_read_cache_bytes = importer.CacheRoot.read_bytes

            def deny_catalog(cache, filename, *args, **kwargs):
                if filename == "catalog.html":
                    raise PermissionError("denied")
                return original_read_cache_bytes(
                    cache,
                    filename,
                    *args,
                    **kwargs,
                )

            with mock.patch.object(
                importer.CacheRoot,
                "read_bytes",
                autospec=True,
                side_effect=deny_catalog,
            ):
                with self.assertRaisesRegex(
                    importer.ImportFailure,
                    "catalog.html.*denied",
                ):
                    importer.run_import(output, client=client)

            self.assertEqual([], opener.requests)
            self.assertEqual(catalog, (output / "catalog.html").read_bytes())

    def test_rejects_noncanonical_slug_before_constructing_path(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            client = importer.ImportClient(opener=RecordingOpener([]))

            with self.assertRaisesRegex(ValueError, "canonical slug"):
                importer.import_pattern(
                    "../escape",
                    output,
                    client,
                    "https://refactoring.guru/design-patterns/state/swift/example",
                    {"patterns": {}},
                )

            self.assertFalse((output.parent / "escape.html").exists())

    def test_rejects_source_url_outside_exact_canonical_origin_and_path(self):
        importer = load_importer()
        invalid_urls = (
            "http://refactoring.guru/design-patterns/state/swift/example",
            "https://evil.test/design-patterns/state/swift/example",
            "https://refactoring.guru/design-patterns/observer/swift/example",
            "https://refactoring.guru:443/design-patterns/state/swift/example",
        )
        with tempfile.TemporaryDirectory() as temporary:
            for source_url in invalid_urls:
                with self.subTest(source_url=source_url):
                    with self.assertRaisesRegex(ValueError, "source URL"):
                        importer.import_pattern(
                            "state",
                            Path(temporary),
                            importer.ImportClient(opener=RecordingOpener([])),
                            source_url,
                            {"patterns": {}},
                        )

    def test_valid_cached_page_is_not_refetched(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            manifest = {"patterns": {"state": write_cached_page(output, "state")}}
            opener = RecordingOpener([])
            client = importer.ImportClient(opener=opener)

            metadata = importer.import_pattern(
                "state",
                output,
                client,
                "https://refactoring.guru/design-patterns/state/swift/example",
                manifest,
            )

            self.assertEqual(manifest["patterns"]["state"], metadata)
            self.assertEqual([], opener.requests)

    def test_checksum_mismatch_triggers_atomic_refetch(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            old_metadata = write_cached_page(output, "state", b"old")
            old_metadata["sha256"] = "incorrect"
            manifest = {"patterns": {"state": old_metadata}}
            opener = RecordingOpener([ByteResponse(b"new")])
            client = importer.ImportClient(opener=opener)

            metadata = importer.import_pattern(
                "state",
                output,
                client,
                "https://refactoring.guru/design-patterns/state/swift/example",
                manifest,
            )

            self.assertEqual(b"new", (output / "state.html").read_bytes())
            self.assertEqual(hashlib.sha256(b"new").hexdigest(), metadata["sha256"])
            self.assertFalse(list(output.glob("*.tmp")))

    def test_refresh_refetches_valid_cached_page(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            manifest = {"patterns": {"state": write_cached_page(output, "state")}}
            opener = RecordingOpener([ByteResponse(b"refreshed")])
            client = importer.ImportClient(opener=opener)

            importer.import_pattern(
                "state",
                output,
                client,
                "https://refactoring.guru/design-patterns/state/swift/example",
                manifest,
                refresh=True,
            )

            self.assertEqual(b"refreshed", (output / "state.html").read_bytes())
            self.assertEqual(1, len(opener.requests))

    def test_load_manifest_returns_safe_empty_shape_for_missing_file(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            self.assertEqual(
                {"catalog": {}, "patterns": {}},
                importer.load_manifest(output),
            )

    def test_corrupt_manifest_raises_without_refetching_or_overwriting_pages(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            cached_page = output / "state.html"
            cached_page.write_bytes(b"preserve me")
            manifest_path = output / "manifest.json"
            manifest_path.write_text("{broken", encoding="utf-8")
            client = importer.ImportClient(opener=RecordingOpener([]))

            with self.assertRaisesRegex(
                importer.ImportFailure,
                "manifest.json",
            ):
                importer.run_import(output, client=client)

            self.assertEqual(b"preserve me", cached_page.read_bytes())
            self.assertEqual("{broken", manifest_path.read_text(encoding="utf-8"))

    def test_wrong_manifest_root_and_io_errors_raise_path_specific_failure(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            manifest_path = output / "manifest.json"
            manifest_path.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(importer.ImportFailure, "manifest.json"):
                importer.load_manifest(output)

            with mock.patch.object(
                importer.CacheRoot,
                "read_bytes",
                autospec=True,
                side_effect=PermissionError("denied"),
            ):
                with self.assertRaisesRegex(
                    importer.ImportFailure,
                    "manifest.json.*denied",
                ):
                    importer.load_manifest(output)


class ImportRunTests(unittest.TestCase):
    def test_attempt_logger_is_scoped_to_each_run(self):
        importer = load_importer()
        catalog = canonical_catalog_html()
        clock = FakeClock()
        persistent_events = []
        responses = []
        for _ in range(2):
            responses.append(ByteResponse(catalog))
            responses.extend(ByteResponse(b"page") for _ in range(22))
        client = importer.ImportClient(
            opener=RecordingOpener(responses),
            monotonic=clock.monotonic,
            sleep=clock.sleep,
            attempt_logger=persistent_events.append,
        )
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            importer.run_import(Path(first), client=client)
            importer.run_import(Path(second), client=client)

            first_lines = (Path(first) / "requests.jsonl").read_text().splitlines()
            second_lines = (Path(second) / "requests.jsonl").read_text().splitlines()

        self.assertEqual(23, len(first_lines))
        self.assertEqual(23, len(second_lines))
        self.assertEqual(46, len(persistent_events))
        self.assertEqual([persistent_events.append], client.attempt_loggers)

    def test_interrupted_refresh_preserves_valid_manifest_page_pairs(self):
        importer = load_importer()
        catalog = canonical_catalog_html()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            output.joinpath("catalog.html").write_bytes(catalog)
            manifest = {
                "catalog": {
                    "sha256": importer.sha256_bytes(catalog),
                    "source_url": load_pattern_catalog().CATALOG_URL,
                },
                "patterns": {},
            }
            for pattern in load_pattern_catalog().PATTERNS:
                manifest["patterns"][pattern.slug] = write_cached_page(
                    output,
                    pattern.slug,
                    content=f"old-{pattern.slug}".encode(),
                    source_url=load_pattern_catalog().pattern_url(pattern.slug),
                )
            output.joinpath("manifest.json").write_text(json.dumps(manifest))
            clock = FakeClock()
            client = importer.ImportClient(
                opener=RecordingOpener(
                    [
                        ByteResponse(catalog),
                        ByteResponse(b"new-abstract-factory"),
                        KeyboardInterrupt(),
                    ]
                ),
                monotonic=clock.monotonic,
                sleep=clock.sleep,
            )

            with self.assertRaises(KeyboardInterrupt):
                importer.run_import(output, refresh=True, client=client)

            resumed = importer.load_manifest(output)
            for pattern in load_pattern_catalog().PATTERNS:
                self.assertTrue(
                    importer.cached_page_is_valid(output, pattern.slug, resumed),
                    pattern.slug,
                )

    def test_invalid_fetched_catalog_is_not_cached_or_manifested(self):
        importer = load_importer()
        client = importer.ImportClient(opener=RecordingOpener([ByteResponse(b"bad")]))
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)

            with self.assertRaisesRegex(ValueError, "missing canonical slugs"):
                importer.run_import(output, client=client)

            self.assertFalse((output / "catalog.html").exists())
            self.assertFalse((output / "manifest.json").exists())

    def test_interruption_preserves_completed_manifest_entry_and_atomic_files(self):
        importer = load_importer()
        catalog = canonical_catalog_html()
        opener = RecordingOpener(
            [
                ByteResponse(catalog),
                ByteResponse(b"first pattern"),
                KeyboardInterrupt(),
            ]
        )
        clock = FakeClock()
        client = importer.ImportClient(
            opener=opener,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)

            with self.assertRaises(KeyboardInterrupt):
                importer.run_import(output, client=client)

            manifest = json.loads(
                (output / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertIn("abstract-factory", manifest["patterns"])
            self.assertEqual(
                b"first pattern",
                (output / "abstract-factory.html").read_bytes(),
            )
            self.assertFalse(list(output.glob("*.tmp")))

    def test_resume_reuses_valid_catalog_and_all_pattern_pages(self):
        importer = load_importer()
        catalog = canonical_catalog_html()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            (output / "catalog.html").write_bytes(catalog)
            manifest = {
                "catalog": {
                    "source_url": load_pattern_catalog().CATALOG_URL,
                    "sha256": importer.sha256_bytes(catalog),
                },
                "patterns": {},
            }
            for pattern in load_pattern_catalog().PATTERNS:
                manifest["patterns"][pattern.slug] = write_cached_page(
                    output,
                    pattern.slug,
                    source_url=load_pattern_catalog().pattern_url(pattern.slug),
                )
            (output / "manifest.json").write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )
            opener = RecordingOpener([])
            client = importer.ImportClient(opener=opener)

            result = importer.run_import(output, client=client)

            self.assertEqual(22, len(result["patterns"]))
            self.assertEqual([], opener.requests)

    def test_writes_request_log_and_required_manifest_metadata(self):
        importer = load_importer()
        catalog = canonical_catalog_html()
        responses = [ByteResponse(catalog)] + [
            ByteResponse(pattern.slug.encode())
            for pattern in load_pattern_catalog().PATTERNS
        ]
        clock = FakeClock()
        client = importer.ImportClient(
            opener=RecordingOpener(responses),
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)

            manifest = importer.run_import(output, client=client)

            self.assertEqual(
                load_pattern_catalog().CATALOG_URL,
                manifest["catalog_url"],
            )
            self.assertEqual(
                load_pattern_catalog().CONTENT_POLICY_URL,
                manifest["content_usage_policy_url"],
            )
            self.assertIn("fetched_at", manifest)
            self.assertEqual(22, len(manifest["patterns"]))
            entry = manifest["patterns"]["state"]
            self.assertEqual(200, entry["http_status"])
            self.assertEqual(len(b"state"), entry["byte_count"])
            log_entries = [
                json.loads(line)
                for line in (output / "requests.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            self.assertEqual(23, len(log_entries))
            self.assertEqual(set(("wall_timestamp", "monotonic", "url", "attempt")), set(log_entries[0]))


class RedirectPolicyTests(unittest.TestCase):
    def test_malformed_redirect_ports_close_response_and_raise_import_failure(self):
        importer = load_importer()
        handler = importer.RestrictedRedirectHandler()
        original = Request("https://refactoring.guru/start")
        for target in (
            "https://refactoring.guru:invalid/target",
            "https://refactoring.guru:99999/target",
        ):
            with self.subTest(target=target):
                response = ByteResponse()

                with self.assertRaisesRegex(importer.ImportFailure, "redirect"):
                    handler.redirect_request(
                        original,
                        response,
                        302,
                        "Found",
                        Message(),
                        target,
                    )

                self.assertTrue(response.closed)

    def test_rejects_cross_origin_ftp_and_http_downgrade_redirects(self):
        importer = load_importer()
        handler = importer.RestrictedRedirectHandler()
        original = Request("https://refactoring.guru/start")
        headers = Message()
        invalid_targets = (
            "https://evil.test/target",
            "ftp://refactoring.guru/target",
            "http://refactoring.guru/target",
        )

        for target in invalid_targets:
            with self.subTest(target=target):
                with self.assertRaisesRegex(importer.ImportFailure, "redirect"):
                    handler.redirect_request(
                        original,
                        None,
                        302,
                        "Found",
                        headers,
                        target,
                    )

    def test_accepted_redirect_hop_is_paced_and_logged_once(self):
        importer = load_importer()
        clock = FakeClock()
        events = []
        client = importer.ImportClient(
            monotonic=clock.monotonic,
            sleep=clock.sleep,
            attempt_logger=events.append,
        )
        sent_urls = []

        class RedirectingHTTPSHandler(HTTPSHandler):
            def https_open(self, request):
                sent_urls.append(request.full_url)
                headers = Message()
                if request.full_url.endswith("/start"):
                    headers["Location"] = (
                        "https://refactoring.guru/design-patterns/state/swift/example"
                    )
                    response = addinfourl(
                        io.BytesIO(),
                        headers,
                        request.full_url,
                        302,
                    )
                    response.msg = "Found"
                    return response
                response = addinfourl(
                    io.BytesIO(b"redirected"),
                    headers,
                    request.full_url,
                    200,
                )
                response.msg = "OK"
                return response

        client.opener = build_opener(
            importer.RestrictedRedirectHandler(),
            importer.OutboundRequestProcessor(
                client._prepare_outbound_request
            ),
            RedirectingHTTPSHandler(),
        )

        content = client.fetch("https://refactoring.guru/start")

        self.assertEqual(b"redirected", content)
        self.assertEqual(
            [
                "https://refactoring.guru/start",
                "https://refactoring.guru/design-patterns/state/swift/example",
            ],
            sent_urls,
        )
        self.assertEqual(sent_urls, [event["url"] for event in events])
        self.assertEqual([5.0], clock.sleeps)
        self.assertEqual([1, 1], [event["attempt"] for event in events])

    def test_redirect_loop_rejection_does_not_log_unsent_hop(self):
        importer = load_importer()
        clock = FakeClock()
        events = []
        client = importer.ImportClient(
            monotonic=clock.monotonic,
            sleep=clock.sleep,
            attempt_logger=events.append,
        )
        sent_urls = []

        class LoopingHTTPSHandler(HTTPSHandler):
            def https_open(self, request):
                sent_urls.append(request.full_url)
                headers = Message()
                headers["Location"] = "https://refactoring.guru/loop"
                response = addinfourl(
                    io.BytesIO(),
                    headers,
                    request.full_url,
                    302,
                )
                response.msg = "Found"
                return response

        client.opener = build_opener(
            importer.RestrictedRedirectHandler(),
            importer.OutboundRequestProcessor(
                client._prepare_outbound_request
            ),
            LoopingHTTPSHandler(),
        )

        with self.assertRaises(HTTPError) as raised:
            client.fetch("https://refactoring.guru/loop")

        self.assertEqual(sent_urls, [event["url"] for event in events])
        self.assertTrue(raised.exception.fp.closed)


class StandardLibraryIntegrationTests(unittest.TestCase):
    observed_intervals = []

    def test_default_interval_spaces_real_local_requests_by_five_seconds(self):
        importer = load_importer()
        timestamps = []

        class TimestampHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                timestamps.append(time.monotonic())
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok")

            def log_message(self, *_):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), TimestampHandler)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            client = importer.ImportClient()
            url = f"http://127.0.0.1:{server.server_port}/page"
            client.fetch(url)
            client.fetch(url)
            self.assertEqual(2, len(timestamps))
            observed_interval = timestamps[1] - timestamps[0]
            type(self).observed_intervals.append(observed_interval)
            self.assertGreaterEqual(observed_interval, 5.0)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
