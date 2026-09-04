"""
foundry/sandbox_runner.py
=========================
FOUNDRY — Docker-based isolated build and test execution.

Provides:
  - `SandboxRunner.ensure_worker_image()` — build the worker image once
  - `SandboxRunner.run(project_dir, command)` — execute a command inside
    a fresh isolated container mounted to the project directory
  - Container is always removed after completion (--rm behaviour)
  - Streams logs in real-time to the genesis logger

Windows notes:
  - Uses `docker.from_env()` which auto-detects the named pipe on Windows
    (npipe:////./pipe/docker_engine) vs. Unix socket on Linux/macOS.
  - Volume paths must be Windows absolute paths when running natively.
"""

from __future__ import annotations

import logging
import os
import platform
from dataclasses import dataclass
from pathlib import Path

try:
    import docker
    import docker.errors
    from docker.models.containers import Container
    _DOCKER_AVAILABLE = True
except ImportError:
    docker = None
    _DOCKER_AVAILABLE = False

from genesis import config

log = logging.getLogger("foundry.sandbox")


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class RunResult:
    exit_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.exit_code == 0


# ---------------------------------------------------------------------------
# Path helpers (Windows ↔ Docker)
# ---------------------------------------------------------------------------

def _to_docker_volume_path(path: Path) -> str:
    """
    Convert an absolute Windows path to the format Docker Desktop expects.
    On Linux/macOS, returns the path unchanged.
    e.g. C:\\Users\\HP\\project → /c/Users/HP/project
    """
    if platform.system() == "Windows":
        # Docker Desktop on Windows uses /drive/path format for bind mounts
        # via the Docker API (npipe) — the Python SDK handles this correctly
        # when we pass the raw Windows path string.
        return str(path)
    return str(path)


# ---------------------------------------------------------------------------
# SandboxRunner
# ---------------------------------------------------------------------------

class SandboxRunner:
    """
    Executes arbitrary shell commands inside an isolated Docker container
    mounted to a project directory.
    """

    def __init__(self) -> None:
        if not _DOCKER_AVAILABLE:
            self._client = None
            return
        try:
            self._client = docker.from_env()
            self._client.ping()
            log.debug("Docker connection OK.")
        except Exception as exc:
            log.error(f"Cannot connect to Docker: {exc}")
            self._client = None

    @staticmethod
    def ensure_worker_image() -> None:
        """
        Build the genesis-worker Docker image if it doesn't already exist.
        Safe to call multiple times (no-op if image is current).
        """
        if not _DOCKER_AVAILABLE:
            log.info("Docker SDK not installed — skipping worker image build (will use local fallback).")
            return
        client = docker.from_env()
        try:
            client.images.get(config.WORKER_IMAGE_NAME)
            log.info(f"Worker image '{config.WORKER_IMAGE_NAME}' already exists.")
            return
        except docker.errors.ImageNotFound:
            pass

        log.info(f"Building worker image '{config.WORKER_IMAGE_NAME}' …")
        context_path = str(Path(config.WORKER_DOCKERFILE).parent)
        try:
            image, build_logs = client.images.build(
                path=context_path,
                dockerfile="Dockerfile.worker",
                tag=config.WORKER_IMAGE_NAME,
                rm=True,
                forcerm=True,
            )
            for log_entry in build_logs:
                if "stream" in log_entry:
                    line = log_entry["stream"].strip()
                    if line:
                        log.debug(f"[docker build] {line}")
            log.info(f"Worker image built successfully: {config.WORKER_IMAGE_NAME}")
        except docker.errors.BuildError as exc:
            log.error(f"Docker build failed: {exc}")
            raise

    def run(
        self,
        project_dir: Path,
        command: str,
        timeout: int = config.CONTAINER_TIMEOUT_SEC,
        environment: dict[str, str] | None = None,
    ) -> RunResult:
        """
        Run `command` inside a fresh worker container with `project_dir`
        bind-mounted to `/project`.

        Returns a RunResult with exit_code, stdout, stderr.
        Container is always removed after completion.
        """
        if self._client is None:
            return self._run_local_fallback(project_dir, command, timeout, environment)

        host_path = _to_docker_volume_path(project_dir.resolve())
        volumes = {host_path: {"bind": "/project", "mode": "rw"}}
        env = environment or {}

        container: Container | None = None
        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        try:
            log.info(f"[Sandbox] Starting container: {command!r}")
            container = self._client.containers.run(
                image=config.WORKER_IMAGE_NAME,
                command=f"bash -c {command!r}",
                volumes=volumes,
                working_dir="/project",
                environment=env,
                detach=True,
                remove=False,       # We remove manually after log capture
                network_mode="bridge",
                mem_limit="512m",   # Memory safety limit
                nano_cpus=int(1e9), # 1 CPU
            )

            # Stream logs in real-time
            for log_chunk in container.logs(stream=True, follow=True):
                line = log_chunk.decode("utf-8", errors="replace").rstrip()
                stdout_lines.append(line)
                log.debug(f"  [container] {line}")

            # Wait for exit
            result = container.wait(timeout=timeout)
            exit_code = result.get("StatusCode", 1)

            # Capture final stderr separately if available
            try:
                stderr_raw = container.logs(stderr=True, stdout=False)
                stderr_lines = stderr_raw.decode("utf-8", errors="replace").splitlines()
            except Exception:
                pass

            log.info(f"[Sandbox] Container exited with code {exit_code}.")
            return RunResult(
                exit_code=exit_code,
                stdout="\n".join(stdout_lines),
                stderr="\n".join(stderr_lines),
            )

        except docker.errors.ContainerError as exc:
            log.error(f"[Sandbox] Container error: {exc}")
            return RunResult(exit_code=1, stdout="", stderr=str(exc))
        except Exception as exc:
            log.error(f"[Sandbox] Unexpected error: {exc}")
            return RunResult(exit_code=1, stdout="", stderr=str(exc))
        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

    def _run_local_fallback(
        self,
        project_dir: Path,
        command: str,
        timeout: int = config.CONTAINER_TIMEOUT_SEC,
        environment: dict[str, str] | None = None,
    ) -> RunResult:
        """
        Heuristic fallback: execute command locally in project_dir when Docker is offline.
        Uses the active virtualenv's Python tools (pip, ruff, pytest).
        """
        import subprocess
        import sys

        log.info(f"[Sandbox/LocalFallback] Docker offline — running natively: {command!r}")
        env = os.environ.copy()
        if environment:
            env.update(environment)

        # Prepend the running Python interpreter's directory (and Scripts on Windows) to PATH
        py_bin = Path(sys.executable).parent
        env["PATH"] = f"{py_bin}{os.pathsep}{env.get('PATH', '')}"
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONPATH"] = f".{os.pathsep}{env.get('PYTHONPATH', '')}"

        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=str(project_dir),
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            return RunResult(
                exit_code=res.returncode,
                stdout=res.stdout,
                stderr=res.stderr,
            )
        except subprocess.TimeoutExpired as exc:
            return RunResult(
                exit_code=124,
                stdout=exc.stdout or "",
                stderr=f"Command timed out after {timeout} seconds",
            )
        except Exception as exc:
            return RunResult(exit_code=1, stdout="", stderr=str(exc))
