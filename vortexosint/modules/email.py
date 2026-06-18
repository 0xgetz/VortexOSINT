"""Email OSINT — syntax validation, Gravatar lookup, MX/deliverability hints
and breach exposure via the free, keyless XposedOrNot public API.
"""
from __future__ import annotations

import hashlib
import re
from typing import Dict, List

from ..core import console, http

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

FREE_PROVIDERS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
    "proton.me", "protonmail.com", "aol.com", "gmx.com", "mail.com", "zoho.com",
}


def _gravatar(email: str, session) -> Dict:
    digest = hashlib.md5(email.strip().lower().encode()).hexdigest()  # noqa: S324 (gravatar spec)
    url = f"https://www.gravatar.com/avatar/{digest}?d=404"
    profile_url = f"https://www.gravatar.com/{digest}.json"
    has_avatar = False
    resp = http.get(session, url)
    if resp is not None:
        has_avatar = resp.status_code == 200
    profile = None
    p = http.get(session, profile_url)
    if p is not None and p.status_code == 200:
        try:
            entries = p.json().get("entry", [])
            if entries:
                e = entries[0]
                profile = {
                    "display_name": e.get("displayName"),
                    "location": e.get("currentLocation"),
                    "about": e.get("aboutMe"),
                    "accounts": [a.get("url") for a in e.get("accounts", [])],
                    "profile_url": e.get("profileUrl"),
                }
        except Exception:  # noqa: BLE001
            profile = None
    return {"hash": digest, "avatar_url": url if has_avatar else None,
            "has_gravatar": has_avatar, "profile": profile}


def _breaches(email: str, session) -> Dict:
    """Query the free, no-key XposedOrNot breach API."""
    url = f"https://api.xposedornot.com/v1/check-email/{email}"
    resp = http.get(session, url)
    if resp is None:
        return {"available": False, "breaches": []}
    if resp.status_code == 404:
        return {"available": True, "breaches": [], "note": "No known breaches"}
    if resp.status_code != 200:
        return {"available": False, "breaches": []}
    try:
        data = resp.json()
        breaches = data.get("breaches", [[]])
        flat: List[str] = breaches[0] if breaches and isinstance(breaches[0], list) else breaches
        return {"available": True, "breaches": flat or [], "count": len(flat or [])}
    except Exception:  # noqa: BLE001
        return {"available": False, "breaches": []}


def investigate(email: str, timeout: int = 15) -> Dict:
    console.section(f"Email scan: {email}")
    session = http.build_session(timeout=timeout)

    valid = bool(EMAIL_RE.match(email))
    domain = email.split("@")[-1].lower() if "@" in email else ""
    is_free = domain in FREE_PROVIDERS

    console.info("Validating syntax & classifying domain...")
    console.kv_panel("Basics", {
        "Email": email,
        "Valid syntax": valid,
        "Domain": domain,
        "Provider type": "Free/consumer" if is_free else "Custom/corporate",
    })

    console.info("Checking Gravatar profile...")
    grav = _gravatar(email, session)
    console.kv_panel("Gravatar", {
        "Has Gravatar": grav["has_gravatar"],
        "Avatar URL": grav["avatar_url"],
        "Display name": (grav.get("profile") or {}).get("display_name"),
        "Linked accounts": ", ".join((grav.get("profile") or {}).get("accounts") or []),
    })

    console.info("Querying public breach data (XposedOrNot)...")
    breach = _breaches(email, session)
    if breach.get("breaches"):
        console.results_table(
            f"Exposed in {breach.get('count', len(breach['breaches']))} breaches",
            ["Breach"], [[b] for b in breach["breaches"]],
        )
    else:
        console.success("No known breaches found in the public dataset.")

    return {
        "email": email,
        "valid_syntax": valid,
        "domain": domain,
        "provider_type": "free" if is_free else "custom",
        "gravatar": grav,
        "breaches": breach,
    }
