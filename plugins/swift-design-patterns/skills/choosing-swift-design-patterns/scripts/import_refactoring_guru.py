#!/usr/bin/env python3
"""Politely and resumably import Swift examples from Refactoring.Guru."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import BaseHandler, HTTPRedirectHandler, Request, build_opener

from pattern_catalog import CATALOG_URL, CONTENT_POLICY_URL, PATTERNS, pattern_url


MINIMUM_INTERVAL = 5.0
DEFAULT_TIMEOUT = 30.0
BACKOFF_BASE = 10.0
MAXIMUM_BACKOFF = 60.0
APPROVED_REDIRECT_HOSTS = frozenset(("refactoring.guru",))
DEFAULT_USER_AGENT = (
    "danny-sung-agent-skills research importer/1.0 "
    "(contact: https://github.com/dannys42/agent-skills)"
)
CANONICAL_SLUGS = frozenset(pattern.slug for pattern in PATTERNS)
SWIFT_EXAMPLE_PATH = re.compile(
    r"^/design-patterns/([a-z-]+)/swift/example$"
)


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


class ImportFailure(Exception):
    """Importer input or persisted state is unsafe to continue from."""


class RestrictedRedirectHandler(HTTPRedirectHandler):
    """Apply urllib redirect semantics, then restrict the resulting origin."""

    def redirect_request(self, request, fp, code, message, headers, new_url):
        redirected_request = super().redirect_request(
            request,
            fp,
            code,
            message,
            headers,
            new_url,
        )
        try:
            parsed_url = urlsplit(redirected_request.full_url)
            allowed = (
                parsed_url.scheme == "https"
                and parsed_url.hostname in APPROVED_REDIRECT_HOSTS
                and parsed_url.port is None
                and parsed_url.username is None
                and parsed_url.password is None
            )
        except ValueError as error:
            if fp is not None:
                fp.close()
            raise ImportFailure(
                f"redirect target is malformed: {redirected_request.full_url}"
            ) from error
        if not allowed:
            if fp is not None:
                fp.close()
            raise ImportFailure(
                f"redirect target is not an approved HTTPS origin: "
                f"{redirected_request.full_url}"
            )
        redirected_request._polite_redirect = True
        return redirected_request


class OutboundRequestProcessor(BaseHandler):
    """Pace redirected requests only when urllib is ready to transmit them."""

    handler_order = 490

    def __init__(self, prepare_outbound_request):
        self.prepare_outbound_request = prepare_outbound_request

    def http_request(self, request):
        return self._prepare(request)

    def https_request(self, request):
        return self._prepare(request)

    def _prepare(self, request):
        if getattr(request, "_polite_prepared", False):
            return request
        self.prepare_outbound_request(
            request.full_url,
            getattr(request, "_polite_redirect", False),
        )
        request._polite_prepared = True
        return request


class ImportClient:
    """HTTP client that enforces a global minimum interval between attempts."""

    def __init__(
        self,
        min_interval=MINIMUM_INTERVAL,
        retries=2,
        opener=None,
        monotonic=time.monotonic,
        sleep=time.sleep,
        attempt_logger=None,
        timeout=DEFAULT_TIMEOUT,
    ):
        if not math.isfinite(min_interval):
            raise ValueError("minimum request interval must be finite")
        if min_interval < MINIMUM_INTERVAL:
            raise ValueError("minimum request interval must be at least 5 seconds")
        if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
            raise ValueError("retries must be a nonnegative integer")
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("timeout must be a finite positive number")
        self.min_interval = float(min_interval)
        self.retries = retries
        self.timeout = float(timeout)
        self.monotonic = monotonic
        self.sleep = sleep
        self.attempt_loggers = []
        if attempt_logger is not None:
            self.attempt_loggers.append(attempt_logger)
        self.last_attempt_monotonic = None
        self.last_status = None
        self.last_response_url = None
        self.current_attempt = None
        self.opener = opener or build_opener(
            RestrictedRedirectHandler(),
            OutboundRequestProcessor(self._prepare_outbound_request),
        )

    def add_attempt_logger(self, logger):
        self.attempt_loggers.append(logger)

    def remove_attempt_logger(self, logger):
        self.attempt_loggers.remove(logger)

    def _pace(self, required_interval):
        now = self.monotonic()
        if self.last_attempt_monotonic is not None:
            elapsed = now - self.last_attempt_monotonic
            remaining = required_interval - elapsed
            if remaining > 0:
                self.sleep(remaining)
                now = self.monotonic()
        self.last_attempt_monotonic = now
        return now

    def _log_attempt(self, url, attempt, monotonic_value):
        entry = {
            "wall_timestamp": utc_timestamp(),
            "monotonic": monotonic_value,
            "url": url,
            "attempt": attempt,
        }
        for logger in self.attempt_loggers:
            logger(dict(entry))

    def _prepare_attempt(self, url, attempt, required_interval):
        attempted_at = self._pace(required_interval)
        self._log_attempt(url, attempt, attempted_at)

    def _prepare_outbound_request(self, url, is_redirect):
        if is_redirect:
            self.last_attempt_monotonic = self.monotonic()
        self._prepare_attempt(
            url,
            self.current_attempt,
            self.min_interval,
        )

    @staticmethod
    def _retry_after(error):
        value = error.headers.get("Retry-After")
        if value is None:
            return 0.0
        try:
            parsed_value = float(value)
        except (TypeError, ValueError):
            return 0.0
        if not math.isfinite(parsed_value) or parsed_value < 0:
            return 0.0
        return parsed_value

    @staticmethod
    def _is_retryable(error):
        if isinstance(error, URLError) and not isinstance(error, HTTPError):
            return True
        return isinstance(error, HTTPError) and (
            error.code == 429 or 500 <= error.code <= 599
        )

    def fetch(self, url):
        required_interval = self.min_interval
        for attempt in range(1, self.retries + 2):
            self.current_attempt = attempt
            self._prepare_attempt(url, attempt, required_interval)
            request = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
            request._polite_prepared = True
            try:
                with self.opener.open(request, timeout=self.timeout) as response:
                    content = response.read()
                    self.last_status = getattr(response, "status", None)
                    if self.last_status is None:
                        self.last_status = response.getcode()
                    response_url = getattr(response, "geturl", None)
                    self.last_response_url = (
                        response_url() if callable(response_url) else None
                    ) or url
                return content
            except (HTTPError, URLError) as error:
                retryable = self._is_retryable(error)
                retry_after = (
                    self._retry_after(error)
                    if isinstance(error, HTTPError)
                    else 0.0
                )
                if isinstance(error, HTTPError):
                    error.close()
                if not retryable or attempt > self.retries:
                    raise
                exponential_backoff = min(
                    BACKOFF_BASE * (2 ** (attempt - 1)),
                    MAXIMUM_BACKOFF,
                )
                required_interval = max(
                    self.min_interval,
                    exponential_backoff,
                    retry_after,
                )
            finally:
                self.last_attempt_monotonic = self.monotonic()
                self.current_attempt = None
        raise RuntimeError("unreachable retry state")


class SwiftExampleLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pattern_urls = {}

    def handle_starttag(self, tag, attributes):
        if tag != "a":
            return
        href = dict(attributes).get("href")
        if href is None:
            return
        try:
            parsed_url = urlsplit(urljoin(CATALOG_URL, href))
            allowed_origin = (
                parsed_url.scheme == "https"
                and parsed_url.hostname == "refactoring.guru"
                and parsed_url.port in (None, 443)
                and parsed_url.username is None
                and parsed_url.password is None
                and not parsed_url.query
            )
        except ValueError:
            return
        if not allowed_origin:
            return
        match = SWIFT_EXAMPLE_PATH.fullmatch(parsed_url.path)
        if match:
            slug = match.group(1)
            self.pattern_urls[slug] = pattern_url(slug)


def discover_pattern_urls(catalog_html):
    if isinstance(catalog_html, bytes):
        catalog_html = catalog_html.decode("utf-8")
    parser = SwiftExampleLinkParser()
    parser.feed(catalog_html)
    canonical_slugs = {pattern.slug for pattern in PATTERNS}
    discovered_slugs = set(parser.pattern_urls)
    missing = sorted(canonical_slugs - discovered_slugs)
    extra = sorted(discovered_slugs - canonical_slugs)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing canonical slugs: {', '.join(missing)}")
        if extra:
            details.append(f"extra noncanonical slugs: {', '.join(extra)}")
        raise ValueError("catalog pattern mismatch; " + "; ".join(details))
    return {slug: parser.pattern_urls[slug] for slug in canonical_slugs}


def sha256_bytes(content):
    return hashlib.sha256(content).hexdigest()


def load_manifest(output):
    manifest_path = Path(output) / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"catalog": {}, "patterns": {}}
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ImportFailure(
            f"cannot load manifest {manifest_path}: {error}"
        ) from error
    if not isinstance(manifest, dict):
        raise ImportFailure(
            f"cannot load manifest {manifest_path}: root must be an object"
        )
    if not isinstance(manifest.get("catalog", {}), dict):
        raise ImportFailure(
            f"cannot load manifest {manifest_path}: catalog must be an object"
        )
    if not isinstance(manifest.get("patterns", {}), dict):
        raise ImportFailure(
            f"cannot load manifest {manifest_path}: patterns must be an object"
        )
    manifest.setdefault("catalog", {})
    manifest.setdefault("patterns", {})
    return manifest


def pattern_page_path(output, slug):
    if slug not in CANONICAL_SLUGS:
        raise ValueError(f"not a canonical slug: {slug}")
    return Path(output) / f"{slug}.html"


def cached_page_is_valid(output, slug, manifest):
    page_path = pattern_page_path(output, slug)
    metadata = manifest.get("patterns", {}).get(slug)
    if not isinstance(metadata, dict):
        return False
    expected_checksum = metadata.get("sha256")
    if not isinstance(expected_checksum, str):
        return False
    try:
        content = page_path.read_bytes()
    except FileNotFoundError:
        return False
    except OSError as error:
        raise ImportFailure(
            f"cannot read cached page {page_path}: {error}"
        ) from error
    return sha256_bytes(content) == expected_checksum


def _atomic_write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary.flush()
            temporary_path = Path(temporary.name)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _atomic_write_json(path, value):
    content = (
        json.dumps(value, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    _atomic_write(path, content)


def _page_metadata(requested_url, final_url, content, status):
    return {
        "source_url": requested_url,
        "requested_url": requested_url,
        "final_url": final_url,
        "fetched_at": utc_timestamp(),
        "http_status": status,
        "byte_count": len(content),
        "sha256": sha256_bytes(content),
    }


def import_pattern(
    slug,
    output,
    client,
    source_url,
    manifest,
    refresh=False,
):
    page_path = pattern_page_path(output, slug)
    expected_url = (
        f"https://refactoring.guru/design-patterns/{slug}/swift/example"
    )
    if source_url != expected_url:
        raise ValueError(
            f"source URL does not match canonical pattern URL for {slug}: "
            f"{source_url}"
        )
    if not refresh and cached_page_is_valid(output, slug, manifest):
        return manifest["patterns"][slug]
    content = client.fetch(source_url)
    _atomic_write(page_path, content)
    return _page_metadata(
        source_url,
        client.last_response_url,
        content,
        client.last_status,
    )


def _catalog_cache_is_valid(output, manifest):
    metadata = manifest.get("catalog")
    if not isinstance(metadata, dict):
        return False
    expected_checksum = metadata.get("sha256")
    if not isinstance(expected_checksum, str):
        return False
    catalog_path = Path(output) / "catalog.html"
    try:
        content = catalog_path.read_bytes()
    except FileNotFoundError:
        return False
    except OSError as error:
        raise ImportFailure(
            f"cannot read cached catalog {catalog_path}: {error}"
        ) from error
    return sha256_bytes(content) == expected_checksum


def _request_log_writer(path):
    def append(entry):
        with path.open("a", encoding="utf-8") as request_log:
            request_log.write(json.dumps(entry, sort_keys=True) + "\n")
            request_log.flush()

    return append


def run_import(
    output,
    min_interval=MINIMUM_INTERVAL,
    refresh=False,
    client=None,
    timeout=DEFAULT_TIMEOUT,
):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(output)
    if client is None:
        client = ImportClient(min_interval=min_interval, timeout=timeout)
    run_logger = _request_log_writer(output / "requests.jsonl")
    client.add_attempt_logger(run_logger)
    try:
        return _run_import(output, refresh, client, manifest)
    finally:
        client.remove_attempt_logger(run_logger)


def _run_import(output, refresh, client, manifest):
    if refresh or not _catalog_cache_is_valid(output, manifest):
        catalog_html = client.fetch(CATALOG_URL)
        pattern_urls = discover_pattern_urls(catalog_html)
        _atomic_write(output / "catalog.html", catalog_html)
        manifest["catalog"] = _page_metadata(
            CATALOG_URL,
            client.last_response_url,
            catalog_html,
            client.last_status,
        )
        manifest["catalog_url"] = CATALOG_URL
        manifest["content_usage_policy_url"] = CONTENT_POLICY_URL
        manifest["fetched_at"] = utc_timestamp()
        _atomic_write_json(output / "manifest.json", manifest)
    else:
        catalog_html = (output / "catalog.html").read_bytes()
        pattern_urls = discover_pattern_urls(catalog_html)

    manifest["catalog_url"] = CATALOG_URL
    manifest["content_usage_policy_url"] = CONTENT_POLICY_URL
    manifest.setdefault(
        "fetched_at",
        manifest.get("catalog", {}).get("fetched_at", utc_timestamp()),
    )
    manifest.setdefault("patterns", {})

    for pattern in PATTERNS:
        metadata = import_pattern(
            pattern.slug,
            output,
            client,
            pattern_urls[pattern.slug],
            manifest,
            refresh=refresh,
        )
        manifest["patterns"][pattern.slug] = metadata
        _atomic_write_json(output / "manifest.json", manifest)
    return manifest


def parse_arguments(arguments=None):
    parser = argparse.ArgumentParser(
        description="Import Refactoring.Guru Swift design-pattern examples.",
    )
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--min-interval",
        type=float,
        default=MINIMUM_INTERVAL,
        metavar="SECONDS",
    )
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        metavar="SECONDS",
    )
    return parser.parse_args(arguments)


def main(arguments=None):
    options = parse_arguments(arguments)
    try:
        run_import(
            options.output,
            min_interval=options.min_interval,
            refresh=options.refresh,
            timeout=options.timeout,
        )
    except KeyboardInterrupt:
        print("Import interrupted; completed pages remain resumable.", file=sys.stderr)
        return 130
    except (
        HTTPError,
        URLError,
        OSError,
        UnicodeError,
        ValueError,
        ImportFailure,
    ) as error:
        print(f"Import failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
