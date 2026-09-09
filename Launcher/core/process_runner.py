# -*- coding: utf-8 -*-
"""Starts a runnable module in its own python process and streams its output.

A separate process is used on purpose:

* the modules print progress, call ``sys.exit`` and open their own Tk window -
  none of that may disturb the launcher window;
* a run can be stopped without leaving a half initialised interpreter behind;
* every run starts from clean configuration state.

The runner is thread safe towards the UI: the reader thread only pushes into a
queue, the Tk main loop drains it (see ``Launcher.ui.app``).
"""
from __future__ import annotations

import codecs
import json
import os
import queue
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any, Mapping, Optional

from .project import PROJECT_ROOT

# message kinds pushed into the queue
MSG_OUTPUT = "output"
MSG_STATUS = "status"
MSG_FINISHED = "finished"

CHILD_MODULE = "Launcher.child_main"


class ProcessRunner:
    """Owns at most one child process at a time."""

    def __init__(self):
        self.queue: "queue.Queue[tuple[str, Any]]" = queue.Queue()
        self._process: Optional[subprocess.Popen] = None
        self._reader: Optional[threading.Thread] = None
        self._overrides_file: Optional[Path] = None
        self._module_id: str = ""
        self._stopping = False

    # --- state --------------------------------------------------------------
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    @property
    def module_id(self) -> str:
        return self._module_id

    # --- control ------------------------------------------------------------
    def start(self, module_id: str, overrides: Mapping[str, Mapping[str, Any]]) -> None:
        if self.is_running():
            raise RuntimeError("a module is already running")

        self._module_id = module_id
        self._stopping = False
        self._overrides_file = self._write_overrides(overrides)

        command = [
            sys.executable,
            "-u",
            "-m",
            CHILD_MODULE,
            module_id,
            str(self._overrides_file),
        ]
        self.queue.put((MSG_STATUS, f"$ {' '.join(command)}"))

        try:
            self._process = subprocess.Popen(
                command,
                cwd=str(PROJECT_ROOT),
                env=self._child_env(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,
                creationflags=self._creation_flags(),
            )
        except Exception as exc:
            self._cleanup_overrides()
            self.queue.put((MSG_OUTPUT, f"Failed to start the module: {exc}\n"))
            self.queue.put((MSG_FINISHED, -1))
            return

        self._reader = threading.Thread(
            target=self._pump_output, name=f"runner-{module_id}", daemon=True
        )
        self._reader.start()

    def stop(self) -> None:
        """Terminate the child process (and whatever it started)."""
        if not self.is_running():
            return
        self._stopping = True
        process = self._process
        assert process is not None
        self.queue.put((MSG_STATUS, "Stopping ..."))
        if os.name == "nt":
            # kill the whole tree, the modules may spawn worker processes
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                capture_output=True,
                check=False,
            )
        else:  # pragma: no cover - project runs on windows
            process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    # --- internals ----------------------------------------------------------
    @staticmethod
    def _creation_flags() -> int:
        if os.name == "nt":
            # do not flash a console window, the output is piped anyway
            return getattr(subprocess, "CREATE_NO_WINDOW", 0)
        return 0

    @staticmethod
    def _child_env() -> dict:
        env = dict(os.environ)
        root = str(PROJECT_ROOT)
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = root + (os.pathsep + existing if existing else "")
        # the modules print emojis - keep them readable through the pipe
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        return env

    def _write_overrides(self, overrides: Mapping[str, Mapping[str, Any]]) -> Path:
        handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", prefix="launcher_cfg_",
            delete=False, encoding="utf-8",
        )
        with handle:
            json.dump(overrides, handle, ensure_ascii=False, default=str)
        return Path(handle.name)

    def _cleanup_overrides(self) -> None:
        if self._overrides_file is not None:
            try:
                self._overrides_file.unlink(missing_ok=True)
            except OSError:
                pass
            self._overrides_file = None

    def _pump_output(self) -> None:
        process = self._process
        assert process is not None
        decoder = codecs.getincrementaldecoder("utf-8")("replace")
        stream = process.stdout
        try:
            while True:
                chunk = stream.read(4096) if stream is not None else b""
                if not chunk:
                    break
                text = decoder.decode(chunk)
                if text:
                    self.queue.put((MSG_OUTPUT, text))
        except Exception as exc:  # pragma: no cover - defensive
            self.queue.put((MSG_OUTPUT, f"\n[launcher] output error: {exc}\n"))
        finally:
            tail = decoder.decode(b"", final=True)
            if tail:
                self.queue.put((MSG_OUTPUT, tail))
            code = process.wait()
            self._cleanup_overrides()
            if self._stopping:
                self.queue.put((MSG_STATUS, "Stopped by the user"))
            self.queue.put((MSG_FINISHED, code))
