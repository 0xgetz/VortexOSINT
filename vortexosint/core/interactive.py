"""Interactive TUI mode for VortexOSINT — a guided menu for users who prefer
not to memorise CLI flags. Built on `rich` prompts with a plain-input fallback.
"""
from __future__ import annotations

from typing import Callable, Dict

from . import console
from ..modules import domain as domain_mod
from ..modules import email as email_mod
from ..modules import exif as exif_mod
from ..modules import ip as ip_mod
from ..modules import phone as phone_mod
from ..modules import username as username_mod
from . import plugins as plugins_mod
from . import report

try:
    from rich.prompt import Prompt, Confirm
    _RICH = True
except Exception:  # pragma: no cover
    _RICH = False


def _ask(prompt: str, default: str = "") -> str:
    if _RICH:
        return Prompt.ask(f"[bold cyan]{prompt}[/bold cyan]", default=default or None) or ""
    raw = input(f"{prompt}{f' [{default}]' if default else ''}: ").strip()
    return raw or default


def _confirm(prompt: str, default: bool = False) -> bool:
    if _RICH:
        return Confirm.ask(f"[bold cyan]{prompt}[/bold cyan]", default=default)
    ans = input(f"{prompt} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
    if not ans:
        return default
    return ans in ("y", "yes")


MENU = """
[bold magenta]VortexOSINT — Interactive Mode[/bold magenta]
  [cyan]1[/cyan]) Username search      [cyan]4[/cyan]) IP geolocation
  [cyan]2[/cyan]) Email investigation  [cyan]5[/cyan]) Phone lookup
  [cyan]3[/cyan]) Domain recon         [cyan]6[/cyan]) Image EXIF
  [cyan]7[/cyan]) Community plugins     [cyan]0[/cyan]) Exit
"""


def _maybe_export(target: str, scan_type: str, data: Dict) -> None:
    if not _confirm("Export this result?", default=False):
        return
    fmt = _ask("Format (json/html/pdf)", default="html").lower()
    safe = "".join(c if c.isalnum() else "_" for c in target)[:40]
    fname = f"vortex_{scan_type}_{safe}"
    try:
        if fmt == "json":
            console.success(f"Saved: {report.to_json(data, fname + '.json')}")
        elif fmt == "pdf":
            console.success(f"Saved: {report.to_pdf(target, scan_type, data, fname + '.pdf')}")
        else:
            console.success(f"Saved: {report.to_html(target, scan_type, data, fname + '.html')}")
    except Exception as exc:  # noqa: BLE001
        console.error(f"Export failed: {exc}")


def run() -> int:
    console.banner("\nWelcome to VortexOSINT interactive mode. Press 0 to quit.\n")
    while True:
        console.banner(MENU)
        choice = _ask("Select an option", default="0").strip()

        if choice == "0":
            console.info("Goodbye! Stay ethical. 👋")
            return 0
        try:
            if choice == "1":
                u = _ask("Username")
                if u:
                    _maybe_export(u, "username", {"username_search": username_mod.search(u)})
            elif choice == "2":
                e = _ask("Email address")
                if e:
                    _maybe_export(e, "email", {"email": email_mod.investigate(e)})
            elif choice == "3":
                d = _ask("Domain")
                if d:
                    deep = _confirm("Enumerate subdomains (slower)?", default=True)
                    _maybe_export(d, "domain", {"domain": domain_mod.investigate(d, deep=deep)})
            elif choice == "4":
                ip = _ask("IP address")
                if ip:
                    _maybe_export(ip, "ip", {"ip": ip_mod.investigate(ip)})
            elif choice == "5":
                p = _ask("Phone number (with country code or set region)")
                region = _ask("Default region (optional, e.g. ID/US)", default="")
                if p:
                    _maybe_export(p, "phone", {"phone": phone_mod.investigate(p, region or None)})
            elif choice == "6":
                path = _ask("Path to image file")
                if path:
                    _maybe_export(path, "exif", {"image": exif_mod.investigate(path)})
            elif choice == "7":
                plugins_mod.list_plugins()
            else:
                console.warn("Invalid choice — pick a number from the menu.")
        except KeyboardInterrupt:
            console.warn("Cancelled. Returning to menu.")
        console.banner("")
