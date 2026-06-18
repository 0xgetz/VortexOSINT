"""Pretty console output with graceful fallback when `rich` is absent."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    _RICH = True
    _console = Console()
except Exception:  # pragma: no cover - rich is a listed dependency
    _RICH = False
    _console = None


def _plain(msg: str) -> None:
    print(msg)


def info(msg: str) -> None:
    if _RICH:
        _console.print(f"[bold cyan][*][/bold cyan] {msg}")
    else:
        _plain(f"[*] {msg}")


def success(msg: str) -> None:
    if _RICH:
        _console.print(f"[bold green][+][/bold green] {msg}")
    else:
        _plain(f"[+] {msg}")


def warn(msg: str) -> None:
    if _RICH:
        _console.print(f"[bold yellow][!][/bold yellow] {msg}")
    else:
        _plain(f"[!] {msg}")


def error(msg: str) -> None:
    if _RICH:
        _console.print(f"[bold red][x][/bold red] {msg}")
    else:
        _plain(f"[x] {msg}")


def banner(text: str) -> None:
    if _RICH:
        _console.print(f"[bold magenta]{text}[/bold magenta]")
    else:
        _plain(text)


def section(title: str) -> None:
    if _RICH:
        _console.rule(f"[bold]{title}")
    else:
        _plain(f"\n==== {title} ====")


def kv_panel(title: str, data: Dict[str, Any]) -> None:
    """Render a key/value mapping as a panel/table."""
    if _RICH:
        table = Table(show_header=False, box=None, pad_edge=False)
        table.add_column("k", style="bold cyan", no_wrap=True)
        table.add_column("v", style="white")
        for k, v in data.items():
            if v in (None, "", [], {}):
                continue
            table.add_row(str(k), str(v))
        _console.print(Panel(table, title=f"[bold]{title}", border_style="cyan"))
    else:
        _plain(f"\n--- {title} ---")
        for k, v in data.items():
            if v in (None, "", [], {}):
                continue
            _plain(f"{k:>18}: {v}")


def results_table(title: str, columns: List[str], rows: List[List[Any]]) -> None:
    if _RICH:
        table = Table(title=f"[bold]{title}", header_style="bold magenta", border_style="dim")
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*[str(c) for c in row])
        _console.print(table)
    else:
        _plain(f"\n=== {title} ===")
        _plain(" | ".join(columns))
        for row in rows:
            _plain(" | ".join(str(c) for c in row))
