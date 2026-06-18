"""Example community plugin: look up the vendor of a MAC address.

Uses the free, keyless maclookup API. Copy this file as a template for your
own plugins. Enable by keeping it in the plugins directory; run with:

    python vortex.py macvendor 00:1A:2B:3C:4D:5E
"""
from __future__ import annotations

from vortexosint.core import console, http


def run(mac: str, **_) -> dict:
    console.section(f"MAC vendor lookup: {mac}")
    session = http.build_session()
    resp = http.get(session, f"https://api.maclookup.app/v2/macs/{mac}")
    if resp is None or resp.status_code != 200:
        console.error("Lookup failed or service unavailable.")
        return {"mac": mac, "found": False}
    try:
        data = resp.json()
    except Exception:  # noqa: BLE001
        return {"mac": mac, "found": False}
    result = {
        "mac": mac,
        "found": bool(data.get("found")),
        "vendor": data.get("company"),
        "address": data.get("address"),
        "country": data.get("country"),
        "block_type": data.get("blockType"),
    }
    console.kv_panel("MAC vendor", result)
    return result


def register():
    return {
        "command": "macvendor",
        "help": "Look up the hardware vendor of a MAC address (community plugin)",
        "args": [{"name": "mac", "help": "MAC address, e.g. 00:1A:2B:3C:4D:5E"}],
        "run": run,
    }
