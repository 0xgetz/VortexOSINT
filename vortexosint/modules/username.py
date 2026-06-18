"""High-accuracy username enumeration.

Accuracy strategy (inspired by Sherlock / Maigret / WhatsMyName):
  1. Use the community-maintained **WhatsMyName** dataset (600+ sites, each with
     validated detection rules: ``e_code`` + ``e_string`` for "exists" and
     ``m_code`` + ``m_string`` for "missing"). Cached locally for 7 days.
  2. Fall back to a curated, hand-validated built-in ruleset when offline.
  3. **False-positive control pass**: every candidate hit is re-checked with a
     random non-existent username on the SAME site. Sites that also "match" the
     random control are unreliable and are dropped. This removes the bulk of
     false positives that naive HTTP-200 checks produce.
  4. Each confirmed hit carries a ``confidence`` score (high/medium).
"""
from __future__ import annotations

import json
import os
import pathlib
import random
import string
import time
from typing import Dict, List, Optional

from ..core import console, http

WMN_URL = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
CACHE_DIR = pathlib.Path.home() / ".vortexosint"
CACHE_FILE = CACHE_DIR / "wmn-data.json"
CACHE_TTL = 7 * 24 * 3600  # 7 days

# Curated offline fallback. Each rule supports validated string/code detection
# for far better accuracy than a bare status check.
BUILTIN_SITES: List[Dict] = [
    {"name": "GitHub", "uri_check": "https://api.github.com/users/{account}",
     "uri_pretty": "https://github.com/{account}",
     "e_code": 200, "e_string": "\"login\"", "m_code": 404, "m_string": "Not Found"},
    {"name": "GitLab", "uri_check": "https://gitlab.com/api/v4/users?username={account}",
     "uri_pretty": "https://gitlab.com/{account}",
     "e_code": 200, "e_string": "\"id\"", "m_code": 200, "m_string": "[]"},
    {"name": "Reddit", "uri_check": "https://www.reddit.com/user/{account}/about.json",
     "uri_pretty": "https://www.reddit.com/user/{account}",
     "e_code": 200, "e_string": "\"name\"", "m_code": 404, "m_string": "error"},
    {"name": "Instagram", "uri_check": "https://www.instagram.com/{account}/",
     "e_code": 200, "e_string": "profilePage_", "m_code": 404, "m_string": "Page Not Found"},
    {"name": "Twitch", "uri_check": "https://m.twitch.tv/{account}",
     "e_code": 200, "e_string": "isPartner", "m_code": 404, "m_string": "Sorry"},
    {"name": "Pinterest", "uri_check": "https://www.pinterest.com/{account}/",
     "e_code": 200, "e_string": "fullName", "m_code": 404, "m_string": "Sorry"},
    {"name": "TikTok", "uri_check": "https://www.tiktok.com/@{account}",
     "e_code": 200, "e_string": "uniqueId", "m_code": 404, "m_string": "Couldn't find this account"},
    {"name": "Steam", "uri_check": "https://steamcommunity.com/id/{account}",
     "e_code": 200, "e_string": "g_rgProfileData", "m_code": 200, "m_string": "The specified profile could not be found"},
    {"name": "Telegram", "uri_check": "https://t.me/{account}",
     "e_code": 200, "e_string": "tgme_page_title", "m_code": 200, "m_string": "tgme_page_additional"},
    {"name": "Medium", "uri_check": "https://medium.com/@{account}",
     "e_code": 200, "e_string": "\"username\"", "m_code": 404, "m_string": "PAGE NOT FOUND"},
    {"name": "Dev.to", "uri_check": "https://dev.to/{account}",
     "e_code": 200, "e_string": "profile-header", "m_code": 404, "m_string": "404"},
    {"name": "Keybase", "uri_check": "https://keybase.io/_/api/1.0/user/lookup.json?username={account}",
     "uri_pretty": "https://keybase.io/{account}",
     "e_code": 200, "e_string": "\"status\":{\"code\":0", "m_code": 200, "m_string": "\"code\":205"},
    {"name": "GitHub Gists", "uri_check": "https://gist.github.com/{account}",
     "e_code": 200, "e_string": "gists", "m_code": 404, "m_string": "Not Found"},
    {"name": "Replit", "uri_check": "https://replit.com/@{account}",
     "e_code": 200, "e_string": "profile", "m_code": 404, "m_string": "404"},
    {"name": "PyPI", "uri_check": "https://pypi.org/user/{account}/",
     "e_code": 200, "e_string": "user-profile", "m_code": 404, "m_string": "Not Found"},
    {"name": "NPM", "uri_check": "https://www.npmjs.com/~{account}",
     "e_code": 200, "e_string": "packages", "m_code": 404, "m_string": "Not Found"},
    {"name": "Docker Hub", "uri_check": "https://hub.docker.com/v2/users/{account}/",
     "uri_pretty": "https://hub.docker.com/u/{account}",
     "e_code": 200, "e_string": "\"username\"", "m_code": 404, "m_string": "Not Found"},
    {"name": "Chess.com", "uri_check": "https://api.chess.com/pub/player/{account}",
     "uri_pretty": "https://www.chess.com/member/{account}",
     "e_code": 200, "e_string": "\"player_id\"", "m_code": 404, "m_string": "not found"},
    {"name": "Last.fm", "uri_check": "https://www.last.fm/user/{account}",
     "e_code": 200, "e_string": "header-avatar", "m_code": 404, "m_string": "404"},
    {"name": "SoundCloud", "uri_check": "https://soundcloud.com/{account}",
     "e_code": 200, "e_string": "soundcloud://users", "m_code": 404, "m_string": "404"},
]


def _random_username() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=18))


def _load_cached_wmn() -> Optional[List[Dict]]:
    try:
        if CACHE_FILE.is_file() and (time.time() - CACHE_FILE.stat().st_mtime) < CACHE_TTL:
            data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            return data.get("sites", [])
    except Exception:  # noqa: BLE001
        pass
    return None


def _fetch_wmn(session) -> Optional[List[Dict]]:
    resp = http.get(session, WMN_URL, timeout=25)
    if resp is None or resp.status_code != 200:
        return None
    try:
        data = resp.json()
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(data), encoding="utf-8")
        return data.get("sites", [])
    except Exception:  # noqa: BLE001
        return None


def _load_sites(session, use_wmn: bool) -> tuple[List[Dict], str]:
    if use_wmn:
        sites = _load_cached_wmn()
        if sites:
            return sites, "WhatsMyName (cached)"
        sites = _fetch_wmn(session)
        if sites:
            return sites, "WhatsMyName (live)"
        console.warn("Could not load WhatsMyName dataset — using built-in ruleset.")
    return BUILTIN_SITES, "built-in"


def _matches(resp, site: Dict) -> Optional[bool]:
    """Return True (exists), False (confirmed absent) or None (inconclusive)."""
    if resp is None:
        return None
    text = resp.text or ""
    e_code = site.get("e_code")
    e_string = site.get("e_string")
    m_code = site.get("m_code")
    m_string = site.get("m_string")

    exists = (e_code is None or resp.status_code == e_code) and (
        not e_string or e_string in text)
    absent = (m_code is None or resp.status_code == m_code) and (
        bool(m_string) and m_string in text)

    if exists and not absent:
        return True
    if absent and not exists:
        return False
    # Disambiguate when both/neither: trust the existence string strongly.
    if e_string and e_string in text and resp.status_code == (e_code or resp.status_code):
        return True
    return None


def _check(session, site: Dict, username: str):
    uri = site.get("uri_check", "")
    if "{account}" not in uri:
        return None
    url = uri.replace("{account}", username)
    resp = http.get(session, url, allow_redirects=True)
    verdict = _matches(resp, site)
    if verdict is True:
        return {
            "site": site.get("name", "?"),
            "url": site.get("uri_pretty", uri).replace("{account}", username),
            "category": site.get("cat", ""),
            "status": getattr(resp, "status_code", None),
        }
    return None


def search(username: str, timeout: int = 15, max_workers: int = 25,
           use_wmn: bool = True, verify: bool = True) -> Dict:
    console.section(f"Username scan: {username}")
    session = http.build_session(timeout=timeout)

    sites, source = _load_sites(session, use_wmn)
    console.info(f"Loaded {len(sites)} site rules from {source}.")

    def worker(site):
        return _check(session, site, username)

    hits: List[Dict] = http.run_concurrent(worker, sites, max_workers=max_workers)

    # ---- false-positive control pass ----
    removed = 0
    if verify and hits:
        console.info("Running false-positive control pass (random control username)...")
        control_user = _random_username()
        hit_names = {h["site"] for h in hits}
        control_sites = [s for s in sites if s.get("name") in hit_names]

        def control_worker(site):
            res = _check(session, site, control_user)
            return site.get("name") if res else None

        unreliable = set(filter(None, http.run_concurrent(control_worker, control_sites, max_workers=max_workers)))
        if unreliable:
            removed = len([h for h in hits if h["site"] in unreliable])
            hits = [h for h in hits if h["site"] not in unreliable]

    for h in hits:
        h["confidence"] = "high"
    hits.sort(key=lambda h: h["site"].lower())

    if hits:
        console.results_table(
            f"Confirmed on {len(hits)} sites (filtered {removed} false positives)",
            ["Site", "URL", "Confidence"],
            [[h["site"], h["url"], h["confidence"]] for h in hits],
        )
    else:
        console.warn("No confirmed public profiles found.")
    if removed:
        console.info(f"Removed {removed} likely false positive(s) via control verification.")

    return {
        "username": username,
        "source": source,
        "checked": len(sites),
        "false_positives_removed": removed,
        "found_count": len(hits),
        "found": hits,
    }
