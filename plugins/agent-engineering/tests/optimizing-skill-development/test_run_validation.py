import contextlib
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from support import load_script


optimizer_config = load_script("optimizer_config")
sys.modules.setdefault("optimizer_config", optimizer_config)
run_validation = load_script("run_validation")


class ValidationRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary_directory.name)
        (self.repository / "work").mkdir()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def command(
        self,
        identifier,
        argv,
        *,
        cwd=None,
        timeout=2,
        limit=1024,
        network=False,
        timing_kind="work",
    ):
        return optimizer_config.Command(
            identifier=identifier,
            argv=tuple(argv),
            cwd=cwd or self.repository / "work",
            timeout_seconds=timeout,
            max_output_bytes=limit,
            network=network,
            timing_kind=timing_kind,
        )

    def config(self, commands, profile=("one",)):
        return optimizer_config.OptimizerConfig(
            path=self.repository / "optimizer.json",
            repository_root=self.repository.resolve(),
            target_root=(self.repository / "work").resolve(),
            includes=(),
            excludes=(),
            commands={command.identifier: command for command in commands},
            profiles={"quick": tuple(profile)},
            evaluations=optimizer_config.Evaluations(
                cases=self.repository / "cases.json",
                rubric=self.repository / "rubric.md",
            ),
        )

    def open_descriptor_set(self):
        descriptors = set()
        for descriptor in range(3, 512):
            try:
                os.fstat(descriptor)
            except OSError:
                continue
            descriptors.add(descriptor)
        return descriptors

    def test_read_bounded_caps_bytes_and_decodes_invalid_utf8_with_replacement(self):
        stream = io.BytesIO(b"a\xf0\x9f\x92\xa9\xfftail")

        text, truncated = run_validation._read_bounded(stream, 6)

        self.assertEqual(text, "a💩�")
        self.assertTrue(truncated)

    def test_command_uses_argv_without_shell_and_preserves_declared_cwd_and_order(self):
        touched = self.repository / "touched"
        script = (
            "import os,sys;"
            "print(os.getcwd());"
            "print('|'.join(sys.argv[1:]))"
        )
        command = self.command(
            "one",
            [sys.executable, "-c", script, f"x; touch {touched}", "second"],
        )

        result = run_validation.run_command(command, allow_network=False)

        self.assertEqual(result["status"], "passed")
        self.assertEqual(
            result["stdout"].splitlines(),
            [str((self.repository / "work").resolve()), f"x; touch {touched}|second"],
        )
        self.assertFalse(touched.exists())
        self.assertEqual(
            set(result),
            {
                "id",
                "status",
                "duration_seconds",
                "exit_code",
                "stdout",
                "stderr",
                "stdout_truncated",
                "stderr_truncated",
                "timing_kind",
            },
        )

    def test_command_reports_failure_and_exact_bounded_stdout_and_stderr(self):
        script = (
            "import os,sys;"
            "os.write(1,b'abcdef');"
            "os.write(2,b'12\\xff456');"
            "sys.exit(7)"
        )
        result = run_validation.run_command(
            self.command("one", [sys.executable, "-c", script], limit=4),
            allow_network=False,
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["exit_code"], 7)
        self.assertEqual(result["stdout"], "abcd")
        self.assertEqual(result["stderr"], "12�4")
        self.assertTrue(result["stdout_truncated"])
        self.assertTrue(result["stderr_truncated"])

    @unittest.skipUnless(os.name == "posix", "requires descriptor cwd launch")
    def test_missing_executable_is_validation_error_without_fd_drift(self):
        success = self.command("success", [sys.executable, "-c", "pass"])
        real_exit_127 = self.command(
            "exit-127",
            [sys.executable, "-c", "raise SystemExit(127)"],
        )
        missing = self.command(
            "missing",
            ["skill-optimizer-command-that-does-not-exist"],
        )
        before = self.open_descriptor_set()

        for _ in range(3):
            self.assertEqual(
                run_validation.run_command(success, allow_network=False)["status"],
                "passed",
            )
            with self.assertRaisesRegex(
                run_validation.ValidationError,
                r"^command 'missing' executable is unavailable$",
            ):
                run_validation.run_command(missing, allow_network=False)
        exit_result = run_validation.run_command(
            real_exit_127,
            allow_network=False,
        )
        with self.assertRaisesRegex(
            run_validation.ValidationError,
            r"^command 'missing' executable is unavailable$",
        ):
            run_validation.run_profile(
                self.config([missing], profile=("missing",)),
                "quick",
            )

        self.assertEqual(exit_result["status"], "failed")
        self.assertEqual(exit_result["exit_code"], 127)
        self.assertEqual(self.open_descriptor_set(), before)

    @unittest.skipUnless(os.name == "posix", "requires descriptor cwd launch")
    def test_final_command_inherits_no_wrapper_descriptors(self):
        descriptor_scan = (
            "import os;"
            "leaked=[];"
            "\nfor fd in range(3,512):"
            "\n try: os.fstat(fd)"
            "\n except OSError: continue"
            "\n else: leaked.append(fd)"
            "\nprint(leaked)"
        )

        result = run_validation.run_command(
            self.command("scan", [sys.executable, "-c", descriptor_scan]),
            allow_network=False,
        )

        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["stdout"], "[]\n")

    @unittest.skipUnless(os.name == "posix", "requires isolated POSIX trampoline")
    def test_trampoline_ignores_sitecustomize_and_shares_command_deadline(self):
        hostile = self.repository / "hostile-pythonpath"
        hostile.mkdir()
        marker = self.repository / "site-effect"
        (hostile / "sitecustomize.py").write_text(
            "import time\n"
            f"open({str(marker)!r}, 'w').close()\n"
            "time.sleep(0.8)\n",
            encoding="utf-8",
        )
        command = self.command("slow", ["/bin/sleep", "1"], timeout=0.1)

        started = time.monotonic()
        with mock.patch.dict(os.environ, {"PYTHONPATH": str(hostile)}):
            result = run_validation.run_command(command, allow_network=False)
        elapsed = time.monotonic() - started

        self.assertEqual(result["status"], "timed_out")
        self.assertLess(elapsed, 0.6)
        self.assertFalse(marker.exists())

    @unittest.skipUnless(os.name == "posix", "requires concurrent pipe drains")
    def test_large_stdout_and_stderr_are_drained_with_bounded_memory_no_tempfiles(self):
        script = (
            "import os;"
            "chunk=b'x'*65536;"
            "\nfor _ in range(128): os.write(1,chunk)"
            "\nfor _ in range(128): os.write(2,chunk)"
        )
        before_threads = {thread.ident for thread in threading.enumerate()}
        started = time.monotonic()
        with mock.patch(
            "tempfile.TemporaryFile",
            side_effect=AssertionError("temporary capture is forbidden"),
        ):
            result = run_validation.run_command(
                self.command(
                    "large",
                    [sys.executable, "-c", script],
                    timeout=5,
                    limit=1,
                ),
                allow_network=False,
            )
        elapsed = time.monotonic() - started

        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["stdout"], "x")
        self.assertEqual(result["stderr"], "x")
        self.assertTrue(result["stdout_truncated"])
        self.assertTrue(result["stderr_truncated"])
        self.assertLess(elapsed, 5)
        self.assertEqual(
            {thread.ident for thread in threading.enumerate()},
            before_threads,
        )

    @unittest.skipUnless(os.name == "posix", "requires concurrent pipe drains")
    def test_interleaved_output_is_drained_when_command_times_out(self):
        script = (
            "import os,time;"
            "\nfor _ in range(4096):"
            "\n os.write(1,b'out!');os.write(2,b'err!')"
            "\ntime.sleep(1)"
        )

        result = run_validation.run_command(
            self.command(
                "chatty",
                [sys.executable, "-c", script],
                timeout=0.1,
                limit=8,
            ),
            allow_network=False,
        )

        self.assertEqual(result["status"], "timed_out")
        self.assertEqual(result["stdout"], "out!out!")
        self.assertEqual(result["stderr"], "err!err!")
        self.assertTrue(result["stdout_truncated"])
        self.assertTrue(result["stderr_truncated"])

    @unittest.skipUnless(os.name == "posix", "requires POSIX process groups")
    def test_successful_leader_cannot_leave_descendant_holding_pipes(self):
        before_threads = {thread.ident for thread in threading.enumerate()}
        before_descriptors = self.open_descriptor_set()
        markers = []
        captured_stderr = io.StringIO()
        started = time.monotonic()

        with contextlib.redirect_stderr(captured_stderr):
            for index in range(3):
                marker = self.repository / f"descendant-{index}"
                markers.append(marker)
                child = (
                    "import time;"
                    "time.sleep(0.7);"
                    f"open({str(marker)!r},'w').close()"
                )
                leader = (
                    "import subprocess,sys;"
                    f"subprocess.Popen([sys.executable,'-c',{child!r}]);"
                    "print('leader')"
                )
                result = run_validation.run_command(
                    self.command(
                        f"leader-{index}",
                        [sys.executable, "-c", leader],
                        timeout=0.2,
                    ),
                    allow_network=False,
                )
                self.assertEqual(result["status"], "passed")
                self.assertEqual(result["stdout"], "leader\n")

        elapsed = time.monotonic() - started
        time.sleep(0.8)

        self.assertLess(elapsed, 0.8)
        self.assertFalse(any(marker.exists() for marker in markers))
        self.assertNotIn("Exception in thread", captured_stderr.getvalue())
        self.assertEqual(
            {thread.ident for thread in threading.enumerate()},
            before_threads,
        )
        self.assertEqual(self.open_descriptor_set(), before_descriptors)

    @unittest.skipUnless(os.name == "posix", "requires detached POSIX child")
    def test_detached_pipe_holder_cannot_extend_deadline_or_leak_parent_resources(self):
        pid_path = self.repository / "detached.pid"
        marker = self.repository / "detached-marker"
        child = (
            "import os,time;"
            f"open({str(pid_path)!r},'w').write(str(os.getpid()));"
            "time.sleep(1.5);"
            f"open({str(marker)!r},'w').close()"
        )
        leader = (
            "import subprocess,sys;"
            f"subprocess.Popen([sys.executable,'-c',{child!r}],"
            "start_new_session=True);"
            "print('leader')"
        )
        command = self.command(
            "detached",
            [sys.executable, "-c", leader],
            timeout=0.2,
            limit=3,
        )
        before_threads = {thread.ident for thread in threading.enumerate()}
        before_descriptors = self.open_descriptor_set()
        captured_stderr = io.StringIO()

        started = time.monotonic()
        with contextlib.redirect_stderr(captured_stderr):
            result = run_validation.run_command(command, allow_network=False)
        elapsed = time.monotonic() - started

        try:
            self.assertEqual(result["status"], "timed_out")
            self.assertEqual(result["stdout"], "lea")
            self.assertTrue(result["stdout_truncated"])
            self.assertLess(elapsed, 0.8)
            self.assertFalse(marker.exists())
            self.assertNotIn("Exception in thread", captured_stderr.getvalue())
            self.assertEqual(
                {thread.ident for thread in threading.enumerate()},
                before_threads,
            )
            self.assertEqual(self.open_descriptor_set(), before_descriptors)
        finally:
            if pid_path.exists():
                detached_pid = int(pid_path.read_text(encoding="utf-8"))
                try:
                    os.kill(detached_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                cleanup_deadline = time.monotonic() + 0.5
                detached_exists = True
                while time.monotonic() < cleanup_deadline:
                    try:
                        os.kill(detached_pid, 0)
                    except ProcessLookupError:
                        detached_exists = False
                        break
                    time.sleep(0.01)
                self.assertFalse(detached_exists, "detached test child was not reaped")

    @unittest.skipUnless(os.name == "posix", "requires secure capability gate")
    def test_missing_secure_capabilities_fail_before_spawn(self):
        command = self.command("one", [sys.executable, "-c", "pass"])
        with (
            mock.patch.object(run_validation.os, "O_NOFOLLOW", 0),
            mock.patch.object(run_validation.subprocess, "Popen") as popen,
        ):
            with self.assertRaises(run_validation.ValidationError):
                run_validation.run_command(command, allow_network=False)
            popen.assert_not_called()

        with (
            mock.patch.object(
                run_validation,
                "_POPEN_SECURE_OPTIONS_AVAILABLE",
                False,
            ),
            mock.patch.object(run_validation.subprocess, "Popen") as popen,
        ):
            with self.assertRaises(run_validation.ValidationError):
                run_validation.run_command(command, allow_network=False)
            popen.assert_not_called()

    def test_network_command_requires_approval_without_starting_process(self):
        marker = self.repository / "marker"
        command = self.command(
            "network",
            [sys.executable, "-c", f"open({str(marker)!r},'w').close()"],
            network=True,
            timing_kind="mandatory_wait",
        )

        blocked = run_validation.run_command(command, allow_network=False)
        self.assertFalse(marker.exists())
        allowed = run_validation.run_command(command, allow_network=True)

        self.assertEqual(blocked["status"], "approval_required")
        self.assertEqual(blocked["duration_seconds"], 0)
        self.assertIsNone(blocked["exit_code"])
        self.assertEqual(blocked["stdout"], "")
        self.assertEqual(allowed["status"], "passed")
        self.assertTrue(marker.exists())

    @unittest.skipUnless(os.name == "posix", "requires POSIX process groups")
    def test_timeout_kills_process_tree_before_child_writes_delayed_marker(self):
        marker = self.repository / "late-marker"
        script = (
            "import subprocess,sys,time;"
            "subprocess.Popen([sys.executable,'-c',"
            f"\"import time;time.sleep(1.4);open({str(marker)!r},'w').close()\""
            "]);"
            "time.sleep(5)"
        )
        command = self.command(
            "slow",
            [sys.executable, "-c", script],
            timeout=1,
        )

        result = run_validation.run_command(command, allow_network=False)
        time.sleep(0.6)

        self.assertEqual(result["status"], "timed_out")
        self.assertIsNone(result["exit_code"])
        self.assertFalse(marker.exists())

    @unittest.skipUnless(os.name == "posix", "requires descriptor cwd launch")
    def test_profile_uses_pinned_cwd_when_path_swaps_before_spawn(self):
        cwd = self.repository / "swappable"
        cwd.mkdir()
        held = self.repository / "held"
        outside_directory = tempfile.TemporaryDirectory()
        self.addCleanup(outside_directory.cleanup)
        outside = Path(outside_directory.name)
        command = self.command(
            "one",
            [
                sys.executable,
                "-c",
                "from pathlib import Path;Path('marker').write_text('ran')",
            ],
            cwd=cwd.resolve(),
        )
        config = self.config([command])
        real_popen = run_validation.subprocess.Popen
        swapped = False

        def swap_then_spawn(*args, **kwargs):
            nonlocal swapped
            if not swapped:
                cwd.rename(held)
                cwd.symlink_to(outside, target_is_directory=True)
                swapped = True
            return real_popen(*args, **kwargs)

        with mock.patch.object(
            run_validation.subprocess, "Popen", side_effect=swap_then_spawn
        ):
            report = run_validation.run_profile(config, "quick")

        self.assertEqual(report["status"], "passed")
        self.assertTrue((held / "marker").exists())
        self.assertFalse((outside / "marker").exists())
        cwd.unlink()

    def test_profile_runs_declared_order_and_stops_or_continues_after_failure(self):
        first = self.command("first", [sys.executable, "-c", "raise SystemExit(3)"])
        second = self.command("second", [sys.executable, "-c", "print('second')"])
        config = self.config([first, second], profile=("first", "second"))

        stopped = run_validation.run_profile(config, "quick")
        continued = run_validation.run_profile(
            config, "quick", continue_on_failure=True
        )

        self.assertEqual([item["id"] for item in stopped["commands"]], ["first"])
        self.assertEqual(stopped["status"], "failed")
        self.assertEqual(
            [item["id"] for item in continued["commands"]], ["first", "second"]
        )
        self.assertEqual(continued["status"], "failed")

    def test_profile_preflights_missing_and_empty_profiles(self):
        command = self.command("one", [sys.executable, "-c", "pass"])
        missing = self.config([command], profile=("missing",))
        empty = self.config([command], profile=())

        with self.assertRaisesRegex(
            run_validation.ValidationError,
            r"^profile 'quick' references unavailable command 'missing'$",
        ):
            run_validation.run_profile(missing, "quick")
        with self.assertRaisesRegex(
            run_validation.ValidationError, r"^profile 'quick' has no commands$"
        ):
            run_validation.run_profile(empty, "quick")
        with self.assertRaisesRegex(
            run_validation.ValidationError, r"^profile 'absent' is unavailable$"
        ):
            run_validation.run_profile(missing, "absent")

    def test_profile_uses_clock_per_executed_command_and_clamps_regression(self):
        first = self.command("first", [sys.executable, "-c", "pass"])
        second = self.command("second", [sys.executable, "-c", "pass"])
        values = iter((10, 10.25, 11, 11.5))
        report = run_validation.run_profile(
            self.config([first, second], profile=("first", "second")),
            "quick",
            clock=lambda: next(values),
        )
        regression = iter((8, 7))
        command_report = run_validation.run_command(
            first, False, clock=lambda: next(regression)
        )

        self.assertEqual(
            [item["duration_seconds"] for item in report["commands"]],
            [0.25, 0.5],
        )
        self.assertEqual(report["duration_seconds"], 0.75)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["schema_version"], 1)
        self.assertRegex(report["generated_at"], r"^\d{4}-\d\d-\d\dT.*Z$")
        self.assertEqual(command_report["duration_seconds"], 0)

    @unittest.skipUnless(hasattr(os, "symlink"), "requires symlinks")
    def test_profile_rejects_cwd_changed_to_escape_after_config_load(self):
        outside = Path(self.temporary_directory.name + "-outside")
        outside.mkdir()
        self.addCleanup(outside.rmdir)
        cwd = self.repository / "swappable"
        cwd.mkdir()
        command = self.command(
            "one", [sys.executable, "-c", "pass"], cwd=cwd.resolve()
        )
        config = self.config([command])
        cwd.rmdir()
        cwd.symlink_to(outside, target_is_directory=True)

        with self.assertRaisesRegex(
            run_validation.ValidationError,
            r"^command 'one' cwd is unavailable or outside repository$",
        ):
            run_validation.run_profile(config, "quick")

        cwd.unlink()

    @unittest.skipUnless(os.name == "posix", "requires repository identity pinning")
    def test_profile_rejects_repository_replacement_after_config_load(self):
        marker_name = "replacement-marker"
        command = self.command(
            "one",
            [
                sys.executable,
                "-c",
                f"open({marker_name!r},'w').close()",
            ],
        )
        repository_stat = self.repository.resolve().stat()
        config = replace(
            self.config([command]),
            repository_identity=(repository_stat.st_dev, repository_stat.st_ino),
        )
        moved = self.repository.with_name(self.repository.name + "-original")
        self.repository.rename(moved)
        self.repository.mkdir()
        (self.repository / "work").mkdir()

        try:
            with self.assertRaises(run_validation.ValidationError):
                run_validation.run_profile(config, "quick")
            self.assertFalse((self.repository / "work" / marker_name).exists())
        finally:
            (self.repository / "work").rmdir()
            self.repository.rmdir()
            moved.rename(self.repository)


class AtomicReportTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.output = self.directory / "report.json"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def assert_no_staging(self):
        self.assertEqual(
            [path.name for path in self.directory.iterdir()],
            ["report.json"] if self.output.exists() else [],
        )

    def test_writer_emits_exact_json_newline_and_leaves_no_staging(self):
        run_validation._write_report_atomic(self.output, {"z": 1, "a": "x"})

        self.assertEqual(self.output.read_bytes(), b'{"a":"x","z":1}\n')
        self.assert_no_staging()

    def test_existing_report_survives_write_fsync_and_replace_failures(self):
        for operation in ("write", "fsync", "replace"):
            with self.subTest(operation=operation):
                self.output.write_text("prior\n", encoding="utf-8")
                target = getattr(run_validation.os, operation)
                with mock.patch.object(
                    run_validation.os,
                    operation,
                    side_effect=OSError("injected"),
                ):
                    with self.assertRaises(run_validation.ValidationError):
                        run_validation._write_report_atomic(self.output, {"new": 1})
                self.assertEqual(self.output.read_text(encoding="utf-8"), "prior\n")
                self.assert_no_staging()

    def test_parent_replacement_during_replace_is_detected_without_false_success(self):
        moved = self.directory.with_name(self.directory.name + "-moved")
        real_replace = run_validation.os.replace
        calls = 0

        def replacing_parent(src, dst, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                os.rename(self.directory, moved)
                self.directory.mkdir()
            return real_replace(src, dst, **kwargs)

        self.addCleanup(lambda: moved.exists() and moved.rename(self.directory))
        with mock.patch.object(run_validation.os, "replace", replacing_parent):
            with self.assertRaises(run_validation.ValidationError):
                run_validation._write_report_atomic(self.output, {"new": 1})

        self.assertFalse(self.output.exists())
        self.assertFalse((moved / "report.json").exists())

    def test_source_substitution_is_detected_without_false_success(self):
        real_replace = run_validation.os.replace

        def substitute(src, dst, **kwargs):
            src_fd = kwargs["src_dir_fd"]
            os.unlink(src, dir_fd=src_fd)
            replacement = os.open(
                src,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=src_fd,
            )
            os.write(replacement, b"substitute\n")
            os.close(replacement)
            return real_replace(src, dst, **kwargs)

        with mock.patch.object(run_validation.os, "replace", substitute):
            with self.assertRaises(run_validation.ValidationError):
                run_validation._write_report_atomic(self.output, {"new": 1})

        self.assertFalse(self.output.exists())
        self.assert_no_staging()

    def test_destination_directory_error_is_controlled_and_path_free(self):
        missing_output = self.directory / "missing" / "report.json"

        with self.assertRaises(run_validation.ValidationError) as caught:
            run_validation._write_report_atomic(missing_output, {"x": 1})

        self.assertNotIn(str(self.directory), str(caught.exception))

    @unittest.skipUnless(os.name == "posix", "requires secure capability gate")
    def test_writer_rejects_missing_nofollow_capability_before_mutation(self):
        self.output.write_text("prior\n", encoding="utf-8")

        with mock.patch.object(run_validation.os, "O_NOFOLLOW", 0):
            with self.assertRaises(run_validation.ValidationError):
                run_validation._write_report_atomic(self.output, {"new": 1})

        self.assertEqual(self.output.read_text(encoding="utf-8"), "prior\n")
        self.assert_no_staging()

    @unittest.skipUnless(os.name == "posix", "requires secure capability gate")
    def test_writer_requires_link_follow_symlink_control_before_mutation(self):
        self.output.write_text("prior\n", encoding="utf-8")
        reduced_support = set(run_validation.os.supports_follow_symlinks)
        reduced_support.discard(run_validation.os.link)

        with mock.patch.object(
            run_validation.os,
            "supports_follow_symlinks",
            reduced_support,
        ):
            with self.assertRaises(run_validation.ValidationError):
                run_validation._write_report_atomic(self.output, {"new": 1})

        self.assertEqual(self.output.read_text(encoding="utf-8"), "prior\n")
        self.assert_no_staging()


class ValidationCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary_directory.name)
        (self.repository / "skill").mkdir()
        subprocess.run(
            ["git", "init", "-q", str(self.repository)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.config_path = self.repository / "optimizer.json"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_config(self, argv):
        command = {
            "argv": argv,
            "cwd": ".",
            "timeout_seconds": 2,
            "max_output_bytes": 1024,
            "network": False,
            "timing_kind": "work",
        }
        config = {
            "schema_version": 1,
            "target": "skill",
            "distributable": {"include": [], "exclude": []},
            "commands": {"one": command},
            "profiles": {
                name: ["one"]
                for name in optimizer_config.PROFILE_NAMES
            },
            "evaluations": {"cases": "cases.json", "rubric": "rubric.md"},
        }
        self.config_path.write_text(json.dumps(config), encoding="utf-8")

    def invoke(self, *arguments):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = run_validation.main(list(arguments))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_cli_stdout_and_exit_codes_are_deterministic(self):
        self.write_config([sys.executable, "-c", "print('ok')"])
        code, stdout, stderr = self.invoke(str(self.config_path), "quick")

        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(stdout, json.dumps(json.loads(stdout), sort_keys=True) + "\n")

        self.write_config([sys.executable, "-c", "raise SystemExit(9)"])
        code, stdout, stderr = self.invoke(str(self.config_path), "quick")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stdout)["status"], "failed")
        self.assertEqual(stderr, "")

    def test_cli_writes_complete_report_and_sanitizes_config_errors(self):
        self.write_config([sys.executable, "-c", "print('ok')"])
        output = self.repository / "out" / "report.json"
        code, stdout, stderr = self.invoke(
            str(self.config_path), "quick", "--output", str(output)
        )
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertNotIn(str(self.repository), stderr)

        output.parent.mkdir()
        code, stdout, stderr = self.invoke(
            str(self.config_path), "quick", "--output", str(output)
        )
        self.assertEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertEqual(json.loads(output.read_text())["status"], "passed")
        self.assertEqual(stderr, "")

        code, _, stderr = self.invoke(
            str(self.repository / "secret-missing.json"), "quick"
        )
        self.assertEqual(code, 2)
        self.assertNotIn(str(self.repository), stderr)

    def test_cli_missing_executable_is_controlled_and_creates_no_report(self):
        self.write_config(["skill-optimizer-command-that-does-not-exist"])
        output = self.repository / "report.json"

        code, stdout, stderr = self.invoke(
            str(self.config_path),
            "quick",
            "--output",
            str(output),
        )

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertFalse(output.exists())
        self.assertNotIn("Traceback", stderr)
        self.assertNotIn(str(self.repository), stderr)
        self.assertEqual(
            stderr,
            "validation error: request could not be completed\n",
        )


if __name__ == "__main__":
    unittest.main()
