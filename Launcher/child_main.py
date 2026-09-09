# -*- coding: utf-8 -*-
"""Entry point of the process that actually runs a module.

Started by :class:`Launcher.core.process_runner.ProcessRunner` as::

    python -u -m Launcher.child_main <module_id> <overrides.json>

It applies the configuration overrides collected in the launcher window and
then calls ``RunnableModule.run()``.  Everything printed here ends up in the
output pane of the launcher.
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

from Launcher.core.project import (
    PROJECT_ROOT,
    ensure_project_root_on_path,
    use_project_root_as_cwd,
)

EXIT_BAD_USAGE = 2
EXIT_UNKNOWN_MODULE = 3
EXIT_FAILED = 1


def _load_overrides(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"[launcher] could not read the overrides file: {exc}")
        return {}


def _add_sys_paths(module) -> None:
    for relative in module.extra_sys_path:
        extra = str((PROJECT_ROOT / relative).resolve())
        if extra not in sys.path:
            sys.path.insert(0, extra)
            print(f"[launcher] sys.path += {relative}")


def _apply_configuration(module, overrides: dict) -> None:
    for source in module.config_sources():
        source_overrides = overrides.get(source.id, {})
        try:
            source.apply(source_overrides)
        except Exception:
            print(f"[launcher] failed to apply '{source.id}':\n{traceback.format_exc()}")
            continue
        if source_overrides:
            print(f"[launcher] {source.title}: {len(source_overrides)} value(s) overridden")
            for key in sorted(source_overrides):
                value = source_overrides[key]
                shown = "***" if _is_secret(source, key) else value
                print(f"[launcher]    {key} = {shown}")
        else:
            print(f"[launcher] {source.title}: file defaults")


def _is_secret(source, name: str) -> bool:
    try:
        for field in source.fields():
            if field.name == name:
                return field.secret
    except Exception:
        pass
    return False


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 1:
        print("usage: python -m Launcher.child_main <module_id> [overrides.json]")
        return EXIT_BAD_USAGE

    module_id = argv[0]
    overrides = _load_overrides(argv[1]) if len(argv) > 1 else {}

    ensure_project_root_on_path()
    use_project_root_as_cwd()

    from Launcher.core.registry import ModuleRegistry

    registry = ModuleRegistry().discover()
    for error in registry.errors:
        print(f"[launcher] module discovery: {error}")

    module = registry.get(module_id)
    if module is None:
        print(f"[launcher] unknown module '{module_id}'")
        return EXIT_UNKNOWN_MODULE

    print(f"[launcher] ===== {module.label()} =====")
    _add_sys_paths(module)
    _apply_configuration(module, overrides)
    print("[launcher] starting ...\n")

    started = time.perf_counter()
    try:
        module.run()
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
        print(f"\n[launcher] module asked to exit with code {code}")
        return code
    except KeyboardInterrupt:
        print("\n[launcher] interrupted")
        return EXIT_FAILED
    except Exception:
        print(f"\n[launcher] module failed:\n{traceback.format_exc()}")
        return EXIT_FAILED
    finally:
        elapsed = time.perf_counter() - started
        print(f"\n[launcher] finished in {elapsed:.3f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
