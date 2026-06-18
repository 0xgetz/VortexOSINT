"""Username enumeration across 40+ free public platforms.

Checks whether a username exists on popular sites by probing public profile
URLs. No API keys, no scraping of private data — only public pages.
"""
from __future__ import annotations

from typing import Dict, List

from ..core import console, http

# site -> {url template, detection method}
# method "status": exists if HTTP 200; "absent_text": exists unless marker present
SITES: Dict[str, Dict] = {
    "GitHub": {"url": "https://github.com/{u}", "method": "status"},
    "GitLab": {"url": "https://gitlab.com/{u}", "method": "status"},
    "Instagram": {"url": "https://www.instagram.com/{u}/", "method": "status"},
    "X (Twitter)": {"url": "https://x.com/{u}", "method": "status"},
    "Reddit": {"url": "https://www.reddit.com/user/{u}", "method": "status"},
    "TikTok": {"url": "https://www.tiktok.com/@{u}", "method": "status"},
    "YouTube": {"url": "https://www.youtube.com/@{u}", "method": "status"},
    "Facebook": {"url": "https://www.facebook.com/{u}", "method": "status"},
    "Pinterest": {"url": "https://www.pinterest.com/{u}/", "method": "status"},
    "Twitch": {"url": "https://www.twitch.tv/{u}", "method": "status"},
    "Steam": {"url": "https://steamcommunity.com/id/{u}", "method": "absent_text",
              "absent": "The specified profile could not be found"},
    "Telegram": {"url": "https://t.me/{u}", "method": "absent_text",
                 "absent": "tgme_page_additional"},
    "Medium": {"url": "https://medium.com/@{u}", "method": "status"},
    "Dev.to": {"url": "https://dev.to/{u}", "method": "status"},
    "Keybase": {"url": "https://keybase.io/{u}", "method": "status"},
    "HackerNews": {"url": "https://news.ycombinator.com/user?id={u}", "method": "absent_text",
                   "absent": "No such user."},
    "Pastebin": {"url": "https://pastebin.com/u/{u}", "method": "status"},
    "SoundCloud": {"url": "https://soundcloud.com/{u}", "method": "status"},
    "Spotify": {"url": "https://open.spotify.com/user/{u}", "method": "status"},
    "Vimeo": {"url": "https://vimeo.com/{u}", "method": "status"},
    "Flickr": {"url": "https://www.flickr.com/people/{u}", "method": "status"},
    "Dribbble": {"url": "https://dribbble.com/{u}", "method": "status"},
    "Behance": {"url": "https://www.behance.net/{u}", "method": "status"},
    "About.me": {"url": "https://about.me/{u}", "method": "status"},
    "Patreon": {"url": "https://www.patreon.com/{u}", "method": "status"},
    "Gravatar": {"url": "https://gravatar.com/{u}", "method": "status"},
    "Replit": {"url": "https://replit.com/@{u}", "method": "status"},
    "CodePen": {"url": "https://codepen.io/{u}", "method": "status"},
    "Bitbucket": {"url": "https://bitbucket.org/{u}/", "method": "status"},
    "DockerHub": {"url": "https://hub.docker.com/u/{u}", "method": "status"},
    "NPM": {"url": "https://www.npmjs.com/~{u}", "method": "status"},
    "PyPI": {"url": "https://pypi.org/user/{u}/", "method": "status"},
    "Wattpad": {"url": "https://www.wattpad.com/user/{u}", "method": "status"},
    "Last.fm": {"url": "https://www.last.fm/user/{u}", "method": "status"},
    "Chess.com": {"url": "https://www.chess.com/member/{u}", "method": "status"},
    "Trello": {"url": "https://trello.com/{u}", "method": "status"},
    "Kaggle": {"url": "https://www.kaggle.com/{u}", "method": "status"},
    "Mastodon (mas.to)": {"url": "https://mas.to/@{u}", "method": "status"},
    "Quora": {"url": "https://www.quora.com/profile/{u}", "method": "status"},
    "VK": {"url": "https://vk.com/{u}", "method": "status"},
    "Roblox": {"url": "https://www.roblox.com/user.aspx?username={u}", "method": "status"},
}


def _check(session, name: str, conf: Dict, username: str):
    url = conf["url"].format(u=username)
    resp = http.get(session, url, allow_redirects=True)
    if resp is None:
        return None
    method = conf.get("method", "status")
    found = False
    if method == "status":
        found = resp.status_code == 200
    elif method == "absent_text":
        found = resp.status_code == 200 and conf.get("absent", "") not in resp.text
    if found:
        return {"site": name, "url": url, "status": resp.status_code}
    return None


def search(username: str, timeout: int = 15, max_workers: int = 25) -> Dict:
    """Search a username across all configured sites concurrently."""
    console.section(f"Username scan: {username}")
    session = http.build_session(timeout=timeout)

    def worker(item):
        name, conf = item
        return _check(session, name, conf, username)

    hits: List[Dict] = http.run_concurrent(worker, list(SITES.items()), max_workers=max_workers)
    hits.sort(key=lambda h: h["site"].lower())

    if hits:
        console.results_table(
            f"Found on {len(hits)}/{len(SITES)} sites",
            ["Site", "URL"],
            [[h["site"], h["url"]] for h in hits],
        )
    else:
        console.warn("No public profiles found on the checked platforms.")

    return {
        "username": username,
        "checked": len(SITES),
        "found_count": len(hits),
        "found": hits,
    }
