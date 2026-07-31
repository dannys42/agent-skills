import contextlib
import hashlib
import io
import json
import os
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from support import SCRIPTS_ROOT, load_script


hash_artifact = load_script("hash_artifact")


def reference_digest(entries):
    digest = hashlib.sha256()
    for path, content in sorted(entries):
        path_bytes = path.encode("utf-8")
        digest.update(struct.pack(">Q", len(path_bytes)))
        digest.update(path_bytes)
        digest.update(struct.pack(">Q", len(content)))
        digest.update(content)
    return digest.hexdigest()


class HashArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary_directory.name)
        subprocess.run(
            ["git", "init", "-q", str(self.repository)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.target = self.repository / "skill"
        self.target.mkdir()
        self.config_path = self.repository / "optimizer.json"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def configuration(self, includes=None, excludes=None):
        return {
            "schema_version": 1,
            "target": "skill",
            "distributable": {
                "include": ["**/*"] if includes is None else includes,
                "exclude": [] if excludes is None else excludes,
            },
            "commands": {},
            "profiles": {
                "quick": [],
                "content": [],
                "behavior": [],
                "importer": [],
                "full": [],
            },
            "evaluations": {
                "cases": "future/cases.json",
                "rubric": "future/rubric.md",
            },
        }

    def write_config(self, includes=None, excludes=None):
        self.config_path.write_text(
            json.dumps(self.configuration(includes, excludes)),
            encoding="utf-8",
        )
        return hash_artifact.optimizer_config.load_config(self.config_path)

    def write_file(self, relative_path, content):
        destination = self.target / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return destination

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPTS_ROOT / "hash_artifact.py"), *arguments],
            cwd=self.repository,
            capture_output=True,
            text=True,
        )

    def test_digest_is_path_order_independent_and_matches_reference(self):
        entries = [("z.txt", b"z"), ("nested/\N{SNOWMAN}.txt", b"\x00payload")]
        expected = reference_digest(entries)

        self.assertEqual(hash_artifact.digest_entries(entries), expected)
        self.assertEqual(hash_artifact.digest_entries(reversed(entries)), expected)
        self.assertEqual(hash_artifact.ALGORITHM, "sha256-length-framed-v1")

    def test_length_framing_distinguishes_boundary_ambiguity(self):
        self.assertNotEqual(
            hash_artifact.digest_entries([("a", b"bc")]),
            hash_artifact.digest_entries([("ab", b"c")]),
        )

    def test_digest_rejects_ambiguous_or_unsafe_paths(self):
        invalid_paths = ("", ".", "./a", "a/../b", "../a", "/a", "a//b", "a\\b", "a\nb")
        for path in invalid_paths:
            with self.subTest(path=path):
                with self.assertRaises(hash_artifact.ArtifactError):
                    hash_artifact.digest_entries([(path, b"value")])

        with self.assertRaises(hash_artifact.ArtifactError):
            hash_artifact.digest_entries([("a", b"one"), ("a", b"two")])
        with self.assertRaises(hash_artifact.ArtifactError):
            hash_artifact.digest_entries([(b"\xff", b"value")])

    def test_selection_sorts_posix_paths_excludes_and_deduplicates_overlaps(self):
        self.write_file("z.txt", b"z")
        self.write_file("docs/a.txt", b"a")
        self.write_file("docs/private.txt", b"secret")
        config = self.write_config(
            ["**/*.txt", "docs/*", "z.txt"],
            ["docs/private.txt"],
        )

        entries = hash_artifact.select_entries(config)

        self.assertEqual(entries, [("docs/a.txt", b"a"), ("z.txt", b"z")])

    def test_excludes_preserve_pure_posix_path_match_semantics(self):
        self.write_file("keep.md", b"keep")
        self.write_file("nested/excluded.txt", b"exclude")
        config = self.write_config(["**/*"], ["*.txt"])

        self.assertEqual(
            hash_artifact.select_entries(config),
            [("keep.md", b"keep")],
        )

    def test_common_recursive_globs_preserve_root_nested_and_wildcard_semantics(self):
        self.write_file("SKILL.md", b"skill")
        self.write_file("agents/root.yaml", b"root")
        self.write_file("agents/nested/child.yaml", b"child")
        self.write_file("references/root.md", b"root reference")
        self.write_file("references/nested/child.md", b"child reference")
        self.write_file("scripts/root.py", b"root script")
        self.write_file("scripts/nested/child.py", b"child script")
        self.write_file("other/ignored.txt", b"ignored")
        config = self.write_config(
            [
                "SKILL.md",
                "agents/**/*.yaml",
                "references/**/*.md",
                "scripts/**/*.py",
                "agent*/**/*.yaml",
                "scripts/**/*.py",
            ]
        )

        self.assertEqual(
            [path for path, _ in hash_artifact.select_entries(config)],
            [
                "SKILL.md",
                "agents/nested/child.yaml",
                "agents/root.yaml",
                "references/nested/child.md",
                "references/root.md",
                "scripts/nested/child.py",
                "scripts/root.py",
            ],
        )

    def test_content_changes_digest_but_executable_mode_does_not(self):
        path = self.write_file("tool.sh", b"first")
        config = self.write_config(["tool.sh"])
        original = hash_artifact.build_manifest(config)["digest"]

        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        executable = hash_artifact.build_manifest(config)["digest"]
        path.write_bytes(b"second")
        changed = hash_artifact.build_manifest(config)["digest"]

        self.assertEqual(executable, original)
        self.assertNotEqual(changed, original)

    def test_same_inode_rewrite_during_read_is_rejected_even_with_restored_mtime(self):
        path = self.write_file("large.bin", b"A" * (2 * 1024 * 1024))
        config = self.write_config(["large.bin"])
        original = path.stat()
        real_read = os.read
        state = {"rewritten": False}

        def rewrite_after_first_chunk(descriptor, size):
            chunk = real_read(descriptor, size)
            if chunk and not state["rewritten"]:
                state["rewritten"] = True
                path.write_bytes(b"B" * (2 * 1024 * 1024))
                os.utime(
                    path,
                    ns=(original.st_atime_ns, original.st_mtime_ns),
                )
            return chunk

        with mock.patch.object(hash_artifact.os, "read", rewrite_after_first_chunk):
            with self.assertRaisesRegex(hash_artifact.ArtifactError, "changed"):
                hash_artifact.select_entries(config)

        self.assertTrue(state["rewritten"])

    def test_empty_selection_is_an_error(self):
        config = self.write_config(["missing-*.txt"])

        with self.assertRaisesRegex(hash_artifact.ArtifactError, "no regular files"):
            hash_artifact.select_entries(config)

    def test_selected_symlink_file_is_rejected_before_outside_bytes_are_read(self):
        outside = self.repository / "outside.txt"
        outside.write_bytes(b"must not be read")
        (self.target / "link.txt").symlink_to(outside)
        config = self.write_config(["link.txt"])

        with mock.patch.object(
            Path,
            "read_bytes",
            side_effect=AssertionError("outside bytes were read"),
        ) as read_bytes:
            with self.assertRaisesRegex(hash_artifact.ArtifactError, "symbolic link"):
                hash_artifact.select_entries(config)
        read_bytes.assert_not_called()

    def test_selected_path_through_symlink_directory_is_rejected_without_reading(self):
        outside = self.repository / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_bytes(b"must not be read")
        (self.target / "linked").symlink_to(outside, target_is_directory=True)
        config = self.write_config(["linked/**/*.txt"])

        with mock.patch.object(
            Path,
            "read_bytes",
            side_effect=AssertionError("outside bytes were read"),
        ) as read_bytes:
            with self.assertRaisesRegex(hash_artifact.ArtifactError, "symbolic link"):
                hash_artifact.select_entries(config)
        read_bytes.assert_not_called()

    def test_recursive_include_rejects_symlink_directory_without_enumerating_outside(self):
        self.write_file("inside.txt", b"inside")
        outside = self.repository / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_bytes(b"must not be discovered")
        (self.target / "linked").symlink_to(outside, target_is_directory=True)
        config = self.write_config(["**/*.txt"])
        real_scandir = os.scandir
        outside_identity = (outside.stat().st_dev, outside.stat().st_ino)
        scanned = []

        def guarded_scandir(path):
            if isinstance(path, int):
                metadata = os.fstat(path)
                identity = (metadata.st_dev, metadata.st_ino)
            else:
                metadata = Path(path).stat()
                identity = (metadata.st_dev, metadata.st_ino)
            scanned.append(identity)
            if identity == outside_identity:
                raise AssertionError("recursive selection entered the symlink target")
            return real_scandir(path)

        with mock.patch.object(hash_artifact.os, "scandir", guarded_scandir):
            with self.assertRaisesRegex(hash_artifact.ArtifactError, "symbolic link"):
                hash_artifact.select_entries(config)

        self.assertNotIn(outside_identity, scanned)

    def test_child_directory_swap_to_outside_symlink_is_rejected_before_scan(self):
        self.write_file("inside.txt", b"inside")
        child = self.target / "child"
        child.mkdir()
        outside = self.repository / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_bytes(b"must not be discovered")
        config = self.write_config(["**/*.txt"])
        real_open = os.open
        real_scandir = os.scandir
        outside_identity = (outside.stat().st_dev, outside.stat().st_ino)
        state = {"swapped": False, "outside_scanned": False}

        def swap_child():
            if not state["swapped"]:
                child.rmdir()
                child.symlink_to(outside, target_is_directory=True)
                state["swapped"] = True

        def swap_then_open(path, flags, *args, **kwargs):
            if path == "child" and kwargs.get("dir_fd") is not None:
                swap_child()
            return real_open(path, flags, *args, **kwargs)

        def guarded_scandir(path):
            if isinstance(path, int):
                metadata = os.fstat(path)
                if (metadata.st_dev, metadata.st_ino) == outside_identity:
                    state["outside_scanned"] = True
            elif Path(path) == child:
                swap_child()
                state["outside_scanned"] = True
            return real_scandir(path)

        with mock.patch.object(
            hash_artifact.os,
            "open",
            swap_then_open,
        ), mock.patch.object(
            hash_artifact.os,
            "scandir",
            guarded_scandir,
        ):
            with self.assertRaises(hash_artifact.ArtifactError):
                hash_artifact.select_entries(config)

        self.assertTrue(state["swapped"])
        self.assertFalse(state["outside_scanned"])

    def test_target_swap_to_outside_symlink_is_rejected_at_repository_boundary(self):
        self.write_file("inside.txt", b"inside")
        config = self.write_config(["**/*.txt"])
        original = self.repository / "original-skill"
        self.target.rename(original)
        outside = self.repository / "outside"
        outside.mkdir()
        secret = outside / "secret.txt"
        secret.write_bytes(b"must not be read")
        self.target.symlink_to(outside, target_is_directory=True)
        outside_identity = (outside.stat().st_dev, outside.stat().st_ino)
        secret_identity = (secret.stat().st_dev, secret.stat().st_ino)
        real_scandir = os.scandir
        real_read = os.read
        state = {"outside_scanned": False, "outside_read": False}

        def guarded_scandir(path):
            metadata = os.fstat(path) if isinstance(path, int) else Path(path).stat()
            if (metadata.st_dev, metadata.st_ino) == outside_identity:
                state["outside_scanned"] = True
            return real_scandir(path)

        def guarded_read(descriptor, size):
            metadata = os.fstat(descriptor)
            if (metadata.st_dev, metadata.st_ino) == secret_identity:
                state["outside_read"] = True
            return real_read(descriptor, size)

        with mock.patch.object(
            hash_artifact.os,
            "scandir",
            guarded_scandir,
        ), mock.patch.object(hash_artifact.os, "read", guarded_read):
            with self.assertRaises(hash_artifact.ArtifactError):
                hash_artifact.select_entries(config)

        self.assertFalse(state["outside_scanned"])
        self.assertFalse(state["outside_read"])

    def test_intermediate_target_swap_to_symlink_is_rejected_before_entering(self):
        container = self.repository / "container"
        container.mkdir()
        self.target.rename(container / "skill")
        self.target = container / "skill"
        configuration = self.configuration(["**/*.txt"])
        configuration["target"] = "container/skill"
        self.config_path.write_text(json.dumps(configuration), encoding="utf-8")
        config = hash_artifact.optimizer_config.load_config(self.config_path)
        original = self.repository / "original-container"
        container.rename(original)
        outside = self.repository / "outside"
        (outside / "skill").mkdir(parents=True)
        (outside / "skill" / "secret.txt").write_bytes(b"must not be read")
        container.symlink_to(outside, target_is_directory=True)
        outside_identity = (
            (outside / "skill").stat().st_dev,
            (outside / "skill").stat().st_ino,
        )
        real_scandir = os.scandir
        scanned = []

        def guarded_scandir(path):
            metadata = os.fstat(path) if isinstance(path, int) else Path(path).stat()
            identity = (metadata.st_dev, metadata.st_ino)
            scanned.append(identity)
            return real_scandir(path)

        with mock.patch.object(hash_artifact.os, "scandir", guarded_scandir):
            with self.assertRaises(hash_artifact.ArtifactError):
                hash_artifact.select_entries(config)

        self.assertNotIn(outside_identity, scanned)

    def test_excluded_symlink_file_and_directory_are_omitted_without_traversal(self):
        self.write_file("inside.txt", b"inside")
        outside = self.repository / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_bytes(b"must not be discovered")
        (self.target / "linked.txt").symlink_to(outside / "secret.txt")
        (self.target / "linked").symlink_to(outside, target_is_directory=True)
        config = self.write_config(
            ["**/*.txt"],
            ["linked.txt", "linked/**"],
        )
        real_scandir = os.scandir
        outside_identity = (outside.stat().st_dev, outside.stat().st_ino)

        def guarded_scandir(path):
            if isinstance(path, int):
                metadata = os.fstat(path)
                identity = (metadata.st_dev, metadata.st_ino)
            else:
                metadata = Path(path).stat()
                identity = (metadata.st_dev, metadata.st_ino)
            if identity == outside_identity:
                raise AssertionError("excluded symlink directory was traversed")
            return real_scandir(path)

        with mock.patch.object(hash_artifact.os, "scandir", guarded_scandir):
            self.assertEqual(
                hash_artifact.select_entries(config),
                [("inside.txt", b"inside")],
            )

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation is unavailable")
    def test_selected_fifo_is_rejected_without_opening(self):
        fifo = self.target / "stream"
        os.mkfifo(fifo)
        config = self.write_config(["stream"])

        with mock.patch.object(
            Path,
            "read_bytes",
            side_effect=AssertionError("FIFO was opened"),
        ) as read_bytes:
            with self.assertRaisesRegex(hash_artifact.ArtifactError, "regular file"):
                hash_artifact.select_entries(config)
        read_bytes.assert_not_called()

    def test_swap_to_outside_symlink_is_rejected_before_outside_bytes_are_read(self):
        victim = self.write_file("victim.txt", b"original")
        outside = self.repository / "outside.txt"
        outside.write_bytes(b"outside bytes")
        config = self.write_config(["victim.txt"])
        real_open = os.open

        def swap_then_open(path, flags, *args, **kwargs):
            if path == "victim.txt" and kwargs.get("dir_fd") is not None:
                victim.unlink()
                victim.symlink_to(outside)
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(hash_artifact.os, "open", swap_then_open):
            with self.assertRaises(hash_artifact.ArtifactError):
                hash_artifact.select_entries(config)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation is unavailable")
    def test_swap_to_fifo_is_rejected_without_blocking(self):
        victim = self.write_file("victim.txt", b"original")
        config = self.write_config(["victim.txt"])
        real_open = os.open

        def swap_then_open(path, flags, *args, **kwargs):
            if path == "victim.txt" and kwargs.get("dir_fd") is not None:
                victim.unlink()
                os.mkfifo(victim)
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(hash_artifact.os, "open", swap_then_open):
            with self.assertRaisesRegex(hash_artifact.ArtifactError, "regular file|changed"):
                hash_artifact.select_entries(config)

    def test_include_patterns_cannot_escape_or_be_absolute(self):
        self.write_file("inside.txt", b"inside")
        outside = self.repository / "outside.txt"
        outside.write_bytes(b"outside")
        for pattern in ("../outside.txt", "/etc/passwd", "docs/../../outside.txt"):
            with self.subTest(pattern=pattern):
                config = self.write_config([pattern])
                with self.assertRaises(hash_artifact.ArtifactError):
                    hash_artifact.select_entries(config)

        config = self.write_config(["**/*.txt"])
        self.assertEqual(hash_artifact.select_entries(config), [("inside.txt", b"inside")])

    def test_manifest_and_cli_json_are_exact_deterministic_and_repository_relative(self):
        self.write_file("b.txt", b"b")
        self.write_file("nested/a.txt", b"a")
        config = self.write_config()
        expected = hash_artifact.build_manifest(config)
        output_path = self.repository / "manifest.json"
        output_path.write_text("old evidence", encoding="utf-8")

        first = self.run_cli(str(self.config_path), "--json", "--output", str(output_path))
        second = self.run_cli(str(self.config_path), "--json")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stdout, json.dumps(expected, sort_keys=True) + "\n")
        self.assertEqual(output_path.read_text(encoding="utf-8"), first.stdout)
        self.assertEqual(
            set(expected),
            {"schema_version", "algorithm", "digest", "target", "files"},
        )
        self.assertEqual(expected["target"], "skill")
        self.assertEqual(
            expected["files"],
            [{"path": "b.txt", "bytes": 1}, {"path": "nested/a.txt", "bytes": 1}],
        )
        self.assertRegex(expected["digest"], r"^[0-9a-f]{64}$")
        self.assertNotIn(str(self.repository), first.stdout)
        self.assertEqual(
            expected["digest"],
            reference_digest([("b.txt", b"b"), ("nested/a.txt", b"a")]),
        )

    def test_output_directory_is_controlled_error_and_existing_file_survives(self):
        self.write_file("file.txt", b"value")
        self.write_config(["file.txt"])
        existing = self.repository / "evidence.json"
        existing.write_text("existing", encoding="utf-8")

        with mock.patch.object(
            hash_artifact.os,
            "replace",
            side_effect=OSError("simulated interruption"),
        ):
            with self.assertRaises(hash_artifact.ArtifactError):
                hash_artifact.write_manifest_atomic(existing, {"digest": "unused"})
        self.assertEqual(existing.read_text(encoding="utf-8"), "existing")
        self.assertEqual(
            [
                path.name
                for path in self.repository.iterdir()
                if path.name.startswith(".evidence.json.")
            ],
            [],
        )

        result = self.run_cli(str(self.config_path), "--output", str(self.repository))
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)

    def test_atomic_output_stays_in_pinned_parent_during_parent_replacement(self):
        parent = self.repository / "evidence"
        parent.mkdir()
        pinned_parent = self.repository / "original-evidence"
        destination = parent / "manifest.json"
        manifest = {
            "schema_version": 1,
            "algorithm": hash_artifact.ALGORITHM,
            "digest": "a" * 64,
            "target": "skill",
            "files": [{"path": "SKILL.md", "bytes": 5}],
        }
        expected = json.dumps(manifest, sort_keys=True) + "\n"
        real_replace = os.replace
        state = {"swapped": False}

        def swap_parent_then_replace(source, target, *args, **kwargs):
            if not state["swapped"]:
                parent.rename(pinned_parent)
                parent.mkdir()
                (parent / "manifest.json").write_text(
                    "attacker bytes",
                    encoding="utf-8",
                )
                state["swapped"] = True
            return real_replace(source, target, *args, **kwargs)

        with mock.patch.object(
            hash_artifact.os,
            "replace",
            swap_parent_then_replace,
        ):
            hash_artifact.write_manifest_atomic(destination, manifest)

        self.assertTrue(state["swapped"])
        self.assertEqual(
            (pinned_parent / "manifest.json").read_text(encoding="utf-8"),
            expected,
        )
        self.assertEqual(
            (parent / "manifest.json").read_text(encoding="utf-8"),
            "attacker bytes",
        )
        self.assertEqual(
            [path.name for path in pinned_parent.iterdir()],
            ["manifest.json"],
        )
        self.assertEqual(
            [path.name for path in parent.iterdir()],
            ["manifest.json"],
        )

    def test_atomic_output_keeps_trusted_inode_pinned_through_replace(self):
        parent = self.repository / "evidence"
        parent.mkdir()
        collision = parent / ".manifest.json.collision.stage"
        collision.mkdir()
        destination = parent / "manifest.json"
        manifest = {
            "schema_version": 1,
            "algorithm": hash_artifact.ALGORITHM,
            "digest": "b" * 64,
            "target": "skill",
            "files": [{"path": "SKILL.md", "bytes": 5}],
        }
        expected = json.dumps(manifest, sort_keys=True) + "\n"
        real_open = os.open
        real_close = os.close
        real_mkdir = os.mkdir
        real_unlink = os.unlink
        real_write = os.write
        tokens = iter(("collision", "trusted"))
        state = {
            "source_fd": None,
            "source_name": None,
            "source_parent_fd": None,
            "substitution_attempted": False,
            "substitution_succeeded": False,
            "mkdir_modes": [],
            "opened_fds": set(),
            "closed_fds": set(),
        }

        def tracked_open(path, flags, *args, **kwargs):
            descriptor = real_open(path, flags, *args, **kwargs)
            state["opened_fds"].add(descriptor)
            if flags & os.O_CREAT and flags & os.O_EXCL:
                state["source_fd"] = descriptor
                state["source_name"] = path
                state["source_parent_fd"] = kwargs.get("dir_fd")
            return descriptor

        def substitute_when_source_descriptor_closes(descriptor):
            if (
                descriptor == state["source_fd"]
                and not state["substitution_attempted"]
            ):
                state["substitution_attempted"] = True
                try:
                    real_unlink(
                        state["source_name"],
                        dir_fd=state["source_parent_fd"],
                    )
                except FileNotFoundError:
                    pass
                else:
                    attacker_fd = real_open(
                        state["source_name"],
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                        0o600,
                        dir_fd=state["source_parent_fd"],
                    )
                    try:
                        real_write(attacker_fd, b"attacker bytes")
                    finally:
                        real_close(attacker_fd)
                    state["substitution_succeeded"] = True
            state["closed_fds"].add(descriptor)
            return real_close(descriptor)

        def tracked_mkdir(path, mode=0o777, *args, **kwargs):
            state["mkdir_modes"].append((path, mode))
            return real_mkdir(path, mode, *args, **kwargs)

        with mock.patch.object(
            hash_artifact.secrets,
            "token_hex",
            side_effect=lambda _: next(tokens),
        ), mock.patch.object(
            hash_artifact.os,
            "open",
            tracked_open,
        ), mock.patch.object(
            hash_artifact.os,
            "close",
            substitute_when_source_descriptor_closes,
        ), mock.patch.object(
            hash_artifact.os,
            "mkdir",
            tracked_mkdir,
        ):
            hash_artifact.write_manifest_atomic(destination, manifest)

        self.assertTrue(state["substitution_attempted"])
        self.assertFalse(state["substitution_succeeded"])
        self.assertEqual(destination.read_text(encoding="utf-8"), expected)
        self.assertIn((".manifest.json.collision.stage", 0o700), state["mkdir_modes"])
        self.assertIn((".manifest.json.trusted.stage", 0o700), state["mkdir_modes"])
        self.assertTrue(state["opened_fds"] <= state["closed_fds"])
        self.assertEqual(
            sorted(path.name for path in parent.iterdir()),
            [".manifest.json.collision.stage", "manifest.json"],
        )

    def test_unreadable_file_has_controlled_path_safe_diagnostic(self):
        self.write_file("private.txt", b"value")
        self.write_config(["private.txt"])
        real_open = os.open

        def deny_selected_file(path, flags, *args, **kwargs):
            if path == "private.txt" and kwargs.get("dir_fd") is not None:
                raise PermissionError("private host detail")
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(
            hash_artifact.os,
            "open",
            side_effect=deny_selected_file,
        ), mock.patch.object(
            Path,
            "read_bytes",
            side_effect=PermissionError("private host detail"),
        ):
            with self.assertRaisesRegex(
                hash_artifact.ArtifactError,
                r"cannot read selected file 'private\.txt'",
            ) as raised:
                hash_artifact.select_entries(
                    hash_artifact.optimizer_config.load_config(self.config_path)
                )
        self.assertNotIn(str(self.repository), str(raised.exception))

    def test_cli_invalid_config_is_controlled_and_has_no_private_absolute_path(self):
        missing = self.repository / "private" / "missing.json"

        result = self.run_cli(str(missing), "--json")

        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn(str(self.repository), result.stderr)
        self.assertIn("missing.json", result.stderr)

    def test_cli_loader_subprocess_failure_is_generic_private_and_controlled(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        error = subprocess.CalledProcessError(
            1,
            ["/private/host/repository/bin/git", "/private/host/repository"],
        )

        with mock.patch.object(
            hash_artifact.optimizer_config,
            "load_config",
            side_effect=error,
        ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = hash_artifact.main(["optimizer.json", "--json"])

        self.assertEqual(result, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertNotIn("/private/host", stderr.getvalue())
        self.assertIn("configuration loading failed", stderr.getvalue())

    def test_cli_loader_os_failure_is_generic_private_and_controlled(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        error = OSError("cannot inspect /private/host/repository")

        with mock.patch.object(
            hash_artifact.optimizer_config,
            "load_config",
            side_effect=error,
        ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = hash_artifact.main(["optimizer.json", "--json"])

        self.assertEqual(result, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertNotIn("/private/host", stderr.getvalue())
        self.assertIn("configuration loading failed", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
