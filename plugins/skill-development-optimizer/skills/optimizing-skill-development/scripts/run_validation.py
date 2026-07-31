#!/usr/bin/env python3

import argparse
import errno
import inspect
import json
import os
import secrets
import selectors
import signal
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Callable

from optimizer_config import Command, ConfigError, OptimizerConfig, load_config


class ValidationError(RuntimeError):
    pass


_EXEC_FROM_FD = (
    "import os,sys\n"
    "directory_fd=int(sys.argv[1])\n"
    "status_fd=int(sys.argv[2])\n"
    "argv=sys.argv[4:]\n"
    "try:\n"
    " os.fchdir(directory_fd)\n"
    " os.close(directory_fd)\n"
    " directory_fd=-1\n"
    " os.set_inheritable(status_fd,False)\n"
    " os.execvp(argv[0],argv)\n"
    "except OSError as error:\n"
    " if directory_fd>=0:\n"
    "  try: os.close(directory_fd)\n"
    "  except OSError: pass\n"
    " try: os.write(status_fd,('E%d' % (error.errno or 0)).encode()[:32])\n"
    " except OSError: pass\n"
    " os._exit(127)\n"
)


def _read_bounded(stream: BinaryIO, limit: int) -> tuple[str, bool]:
    data = stream.read(limit + 1)
    return data[:limit].decode("utf-8", errors="replace"), len(data) > limit


def _empty_result(command: Command, status: str) -> dict:
    return {
        "id": command.identifier,
        "status": status,
        "duration_seconds": 0,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "stdout_truncated": False,
        "stderr_truncated": False,
        "timing_kind": command.timing_kind,
    }


def _directory_open_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )


def _has_parameters(function, names: set[str]) -> bool:
    try:
        return names <= set(inspect.signature(function).parameters)
    except (TypeError, ValueError):
        return False


_POPEN_SECURE_OPTIONS_AVAILABLE = _has_parameters(
    subprocess.Popen,
    {"pass_fds", "start_new_session"},
)
_REPLACE_DIRECTORY_FDS_AVAILABLE = _has_parameters(
    os.replace,
    {"src_dir_fd", "dst_dir_fd"},
)


def _require_descriptor_capabilities() -> None:
    required_flags = ("O_NOFOLLOW", "O_DIRECTORY", "O_CLOEXEC")
    required_dir_fd = (
        os.open,
        os.stat,
        os.mkdir,
        os.unlink,
        os.rmdir,
        os.link,
    )
    if (
        os.name != "posix"
        or any(not getattr(os, name, 0) for name in required_flags)
        or any(function not in os.supports_dir_fd for function in required_dir_fd)
        or os.stat not in os.supports_follow_symlinks
        or os.link not in os.supports_follow_symlinks
        or not _REPLACE_DIRECTORY_FDS_AVAILABLE
    ):
        raise ValidationError("secure descriptor operations are unavailable")


def _open_directory_components(start_fd: int, components: tuple[str, ...]) -> int:
    current_fd = os.dup(start_fd)
    try:
        for component in components:
            before = os.stat(
                component,
                dir_fd=current_fd,
                follow_symlinks=False,
            )
            next_fd = os.open(
                component,
                _directory_open_flags(),
                dir_fd=current_fd,
            )
            opened = os.fstat(next_fd)
            if (
                not stat.S_ISDIR(before.st_mode)
                or not stat.S_ISDIR(opened.st_mode)
                or (before.st_dev, before.st_ino, before.st_mode)
                != (opened.st_dev, opened.st_ino, opened.st_mode)
            ):
                os.close(next_fd)
                raise OSError("directory changed while opening")
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def _require_secure_launch_support() -> None:
    _require_descriptor_capabilities()
    if (
        not hasattr(os, "fchdir")
        or not hasattr(os, "killpg")
        or not _POPEN_SECURE_OPTIONS_AVAILABLE
    ):
        raise ValidationError(
            "secure descriptor-based command launch is unavailable"
        )


def _open_absolute_directory(path: Path) -> int:
    _require_secure_launch_support()
    try:
        resolved_path = path.resolve(strict=True)
    except (OSError, ValueError) as error:
        raise ValidationError("command cwd is unavailable") from error
    if not resolved_path.is_absolute():
        raise ValidationError("command cwd is unavailable")
    root_fd = None
    try:
        root_before = resolved_path.anchor and Path(resolved_path.anchor).lstat()
        root_fd = os.open(resolved_path.anchor, _directory_open_flags())
        root_opened = os.fstat(root_fd)
        if (
            not stat.S_ISDIR(root_before.st_mode)
            or not stat.S_ISDIR(root_opened.st_mode)
            or (
                root_before.st_dev,
                root_before.st_ino,
                root_before.st_mode,
            )
            != (
                root_opened.st_dev,
                root_opened.st_ino,
                root_opened.st_mode,
            )
        ):
            raise OSError("filesystem root changed while opening")
        return _open_directory_components(
            root_fd,
            tuple(resolved_path.parts[1:]),
        )
    except (OSError, ValueError) as error:
        raise ValidationError("command cwd is unavailable") from error
    finally:
        if root_fd is not None:
            os.close(root_fd)


def _open_profile_directory(
    repository_fd: int,
    repository_root: Path,
    command: Command,
) -> int:
    try:
        relative = command.cwd.relative_to(repository_root)
    except ValueError:
        try:
            relative = command.cwd.resolve(strict=True).relative_to(
                repository_root.resolve(strict=True)
            )
        except (OSError, ValueError):
            raise ValidationError(
                f"command '{command.identifier}' cwd is unavailable or outside repository"
            ) from None

    try:
        return _open_directory_components(repository_fd, tuple(relative.parts))
    except (OSError, ValueError) as error:
        raise ValidationError(
            f"command '{command.identifier}' cwd is unavailable or outside repository"
        ) from error


def _kill_process_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired as error:
            raise ValidationError("timed-out command could not be reaped") from error


def _terminate_remaining_process_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def _retain_bounded(buffer: bytearray, data: bytes, capacity: int) -> None:
    remaining = capacity - len(buffer)
    if remaining > 0:
        buffer.extend(data[:remaining])


def _render_retained(buffer: bytearray, limit: int) -> tuple[str, bool]:
    return (
        bytes(buffer[:limit]).decode("utf-8", errors="replace"),
        len(buffer) > limit,
    )


def _run_command_in_directory(
    command: Command,
    clock: Callable[[], float],
    directory_fd: int,
) -> dict:
    process = None
    selector = None
    status_read_fd = -1
    status_write_fd = -1
    stdout_stream = None
    stderr_stream = None
    stdout_buffer = bytearray()
    stderr_buffer = bytearray()
    status_buffer = bytearray()
    try:
        status_read_fd, status_write_fd = os.pipe()
        started = clock()
        deadline = time.monotonic() + command.timeout_seconds
        process = subprocess.Popen(
            (
                sys.executable,
                "-I",
                "-S",
                "-c",
                _EXEC_FROM_FD,
                str(directory_fd),
                str(status_write_fd),
                "--",
                *command.argv,
            ),
            shell=False,
            cwd=None,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            pass_fds=(directory_fd, status_write_fd),
            start_new_session=True,
        )
        os.close(directory_fd)
        directory_fd = -1
        os.close(status_write_fd)
        status_write_fd = -1
        stdout_stream = process.stdout
        stderr_stream = process.stderr
        stdout_fd = stdout_stream.fileno()
        stderr_fd = stderr_stream.fileno()
        for descriptor in (stdout_fd, stderr_fd, status_read_fd):
            os.set_blocking(descriptor, False)
        selector = selectors.DefaultSelector()
        selector.register(stdout_fd, selectors.EVENT_READ, "stdout")
        selector.register(stderr_fd, selectors.EVENT_READ, "stderr")
        selector.register(status_read_fd, selectors.EVENT_READ, "status")

        timed_out = False
        leader_cleanup_done = False
        while True:
            if process.poll() is not None and not leader_cleanup_done:
                _terminate_remaining_process_group(process)
                leader_cleanup_done = True
            if process.returncode is not None and not selector.get_map():
                break

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                if process.poll() is None:
                    _kill_process_group(process)
                else:
                    _terminate_remaining_process_group(process)
                break
            try:
                events = selector.select(timeout=min(remaining, 0.05))
            except InterruptedError:
                continue
            for key, _ in events:
                while True:
                    if time.monotonic() >= deadline:
                        break
                    try:
                        chunk = os.read(key.fd, 65_536)
                    except InterruptedError:
                        continue
                    except BlockingIOError:
                        break
                    except OSError as error:
                        if error.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                            break
                        raise ValidationError(
                            "command output could not be drained"
                        ) from error
                    if not chunk:
                        selector.unregister(key.fd)
                        break
                    if key.data == "stdout":
                        _retain_bounded(
                            stdout_buffer,
                            chunk,
                            command.max_output_bytes + 1,
                        )
                    elif key.data == "stderr":
                        _retain_bounded(
                            stderr_buffer,
                            chunk,
                            command.max_output_bytes + 1,
                        )
                    else:
                        _retain_bounded(status_buffer, chunk, 33)

        if process.poll() is None:
            _kill_process_group(process)
            timed_out = True
        if not leader_cleanup_done:
            _terminate_remaining_process_group(process)
        stdout, stdout_truncated = _render_retained(
            stdout_buffer,
            command.max_output_bytes,
        )
        stderr, stderr_truncated = _render_retained(
            stderr_buffer,
            command.max_output_bytes,
        )
        finished = clock()
        if status_buffer and not timed_out:
            raise ValidationError(
                f"command '{command.identifier}' executable is unavailable"
            )
    except BaseException:
        if process is not None and process.poll() is None:
            _kill_process_group(process)
        if process is not None:
            _terminate_remaining_process_group(process)
        raise
    finally:
        if selector is not None:
            selector.close()
        if stdout_stream is not None:
            stdout_stream.close()
        if stderr_stream is not None:
            stderr_stream.close()
        if directory_fd >= 0:
            os.close(directory_fd)
        if status_write_fd >= 0:
            os.close(status_write_fd)
        if status_read_fd >= 0:
            os.close(status_read_fd)

    if timed_out:
        status = "timed_out"
        exit_code = None
    else:
        exit_code = process.returncode
        status = "passed" if exit_code == 0 else "failed"

    return {
        "id": command.identifier,
        "status": status,
        "duration_seconds": max(0, finished - started),
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
        "timing_kind": command.timing_kind,
    }


def run_command(
    command: Command,
    allow_network: bool,
    clock: Callable[[], float] = time.monotonic,
) -> dict:
    if command.network and not allow_network:
        return _empty_result(command, "approval_required")

    return _run_command_in_directory(
        command,
        clock,
        _open_absolute_directory(command.cwd),
    )


def run_profile(
    config: OptimizerConfig,
    profile: str,
    allow_network: bool = False,
    continue_on_failure: bool = False,
    clock: Callable[[], float] = time.monotonic,
) -> dict:
    if profile not in config.profiles:
        raise ValidationError(f"profile '{profile}' is unavailable")
    command_ids = config.profiles[profile]
    if not command_ids:
        raise ValidationError(f"profile '{profile}' has no commands")
    for command_id in command_ids:
        if command_id not in config.commands:
            raise ValidationError(
                f"profile '{profile}' references unavailable command '{command_id}'"
            )

    repository_fd = _open_absolute_directory(config.repository_root)
    repository_metadata = os.fstat(repository_fd)
    opened_identity = (
        repository_metadata.st_dev,
        repository_metadata.st_ino,
    )
    if (
        config.repository_identity is not None
        and opened_identity != config.repository_identity
    ):
        os.close(repository_fd)
        raise ValidationError("repository root identity changed")

    results = []
    try:
        for command_id in command_ids:
            command = config.commands[command_id]
            if command.network and not allow_network:
                result = _empty_result(command, "approval_required")
            else:
                result = _run_command_in_directory(
                    command,
                    clock,
                    _open_profile_directory(
                        repository_fd,
                        config.repository_root,
                        command,
                    ),
                )
            results.append(result)
            if result["status"] != "passed" and not continue_on_failure:
                break
    finally:
        os.close(repository_fd)

    # Declared order decides precedence: the first blocking result is the
    # profile status, even when later commands are requested for diagnostics.
    status = "passed"
    for result in results:
        if result["status"] != "passed":
            status = result["status"]
            break
    if len(results) != len(command_ids) and status == "passed":
        status = "failed"

    return {
        "schema_version": 1,
        "profile": profile,
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "commands": results,
        "duration_seconds": sum(item["duration_seconds"] for item in results),
    }


def _directory_matches_path(parent: Path, parent_fd: int) -> bool:
    try:
        path_stat = parent.stat()
        fd_stat = os.fstat(parent_fd)
    except OSError:
        return False
    return (path_stat.st_dev, path_stat.st_ino) == (
        fd_stat.st_dev,
        fd_stat.st_ino,
    )


def _remove_if_present(name: str, directory_fd: int) -> None:
    try:
        os.unlink(name, dir_fd=directory_fd)
    except FileNotFoundError:
        pass


def _write_report_atomic(output: Path | str, report: dict) -> None:
    _require_descriptor_capabilities()
    destination = Path(output)
    if (
        destination.name in ("", ".", "..")
        or destination.parent == destination
    ):
        raise ValidationError("report destination is invalid")

    parent_fd = None
    stage_fd = None
    stage_name = f".validation-report-{secrets.token_hex(12)}"
    source_name = "report.json"
    backup_name = "prior.json"
    installed = False
    backup_exists = False
    try:
        parent_fd = os.open(
            destination.parent,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        if not stat.S_ISDIR(os.fstat(parent_fd).st_mode):
            raise OSError("not a directory")
        os.mkdir(stage_name, mode=0o700, dir_fd=parent_fd)
        stage_fd = os.open(
            stage_name,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )

        source_fd = os.open(
            source_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=stage_fd,
        )
        try:
            source_bytes = (
                json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
            ).encode("utf-8")
            offset = 0
            while offset < len(source_bytes):
                written = os.write(source_fd, source_bytes[offset:])
                if written <= 0:
                    raise OSError("short report write")
                offset += written
            os.fsync(source_fd)
            source_identity = os.fstat(source_fd)

            try:
                os.link(
                    destination.name,
                    backup_name,
                    src_dir_fd=parent_fd,
                    dst_dir_fd=stage_fd,
                    follow_symlinks=False,
                )
                backup_exists = True
            except FileNotFoundError:
                pass

            if not _directory_matches_path(destination.parent, parent_fd):
                raise OSError("report parent changed")
            os.replace(
                source_name,
                destination.name,
                src_dir_fd=stage_fd,
                dst_dir_fd=parent_fd,
            )
            installed = True

            installed_fd = os.open(
                destination.name,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=parent_fd,
            )
            try:
                installed_identity = os.fstat(installed_fd)
            finally:
                os.close(installed_fd)
            if (
                source_identity.st_dev,
                source_identity.st_ino,
            ) != (
                installed_identity.st_dev,
                installed_identity.st_ino,
            ):
                raise OSError("report source changed")
            if not _directory_matches_path(destination.parent, parent_fd):
                raise OSError("report parent changed")
            os.fsync(parent_fd)
        except BaseException:
            if installed:
                if backup_exists:
                    os.replace(
                        backup_name,
                        destination.name,
                        src_dir_fd=stage_fd,
                        dst_dir_fd=parent_fd,
                    )
                    backup_exists = False
                else:
                    _remove_if_present(destination.name, parent_fd)
                installed = False
            raise
        finally:
            os.close(source_fd)
    except (OSError, ValueError) as error:
        raise ValidationError("cannot write report safely") from error
    finally:
        if stage_fd is not None:
            _remove_if_present(source_name, stage_fd)
            _remove_if_present(backup_name, stage_fd)
            os.close(stage_fd)
        if parent_fd is not None:
            try:
                os.rmdir(stage_name, dir_fd=parent_fd)
            except FileNotFoundError:
                pass
            os.close(parent_fd)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("profile")
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--continue-on-failure", action="store_true")
    parser.add_argument("--output")
    return parser


def main(argv=None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        config = load_config(arguments.config)
        report = run_profile(
            config,
            arguments.profile,
            allow_network=arguments.allow_network,
            continue_on_failure=arguments.continue_on_failure,
        )
        if arguments.output:
            _write_report_atomic(arguments.output, report)
        else:
            print(json.dumps(report, sort_keys=True))
    except (ConfigError, ValidationError):
        print("validation error: request could not be completed", file=sys.stderr)
        return 2
    except (OSError, subprocess.SubprocessError):
        print("validation error: operation failed", file=sys.stderr)
        return 2
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
