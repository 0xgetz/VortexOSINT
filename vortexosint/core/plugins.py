"""Community plugin system for VortexOSINT.

A plugin is a Python module exposing a top-level ``register()`` function that
returns a dict describing a new command:

    def register():
        return {
            "command": "ipinfo",          # CLI subcommand name
            "help": "Extra IP details",   # short help text
            "args": [                       # positional arguments
                {"name": "ip", "help": "IP address"},
            ],
            "options": [                    # optional flags (optional)
                {"name": "--lang", "help": "language", "default": "en"},
            ],
            "run": run,                     # callable(**kwargs) -> dict
        }

Plugins are discovered from two locations (both optional):
  * the bundled ``vortexosint/plugins/`` directory, and
  * the user directory ``~/.vortexosint/plugins/`` (or ``$VORTEX_PLUGINS``).
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
from typing import Dict, List

from . import console


def _plugin_dirs() -> List[pathlib.Path]:
    dirs = [pathlib.Path(__file__).resolve().parent.parent / "plugins"]
    env = os.environ.get("VORTEX_PLUGINS")
    if env:
        dirs.append(pathlib.Path(env).expanduser())
    dirs.append(pathlib.Path.home() / ".vortexosint" / "plugins")
    return dirs


def _load_module(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(f"vortex_plugin_{path.stem}", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def discover() -> List[Dict]:
    """Discover and validate all available plugins."""
    plugins: List[Dict] = []
    seen = set()
    for directory in _plugin_dirs():
        if not directory.is_dir():
            continue
        for file in sorted(directory.glob("*.py")):
            if file.name.startswith("_"):
                continue
            try:
                module = _load_module(file)
                if module is None or not hasattr(module, "register"):
                    continue
                meta = module.register()
                cmd = meta.get("command")
                if not cmd or cmd in seen or not callable(meta.get("run")):
                    continue
                meta.setdefault("args", [])
                meta.setdefault("options", [])
                meta.setdefault("help", f"Community plugin: {cmd}")
                meta["_source"] = str(file)
                seen.add(cmd)
                plugins.append(meta)
            except Exception as exc:  # noqa: BLE001 - never let a bad plugin crash the tool
                console.warn(f"Failed to load plugin {file.name}: {exc}")
    return plugins


def list_plugins() -> List[Dict]:
    plugins = discover()
    if plugins:
        console.results_table(
            f"Loaded plugins ({len(plugins)})",
            ["Command", "Description", "Source"],
            [[p["command"], p["help"], os.path.basename(p["_source"])] for p in plugins],
        )
    else:
        console.info("No community plugins installed. Drop a .py file in "
                     "~/.vortexosint/plugins/ to add one.")
    return plugins
