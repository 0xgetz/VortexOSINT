"""Shared HTTP client with sane defaults, retries and concurrency helpers.

Only uses free, public, keyless endpoints. No API keys required.
"""
from __future__ import annotations

import concurrent.futures as cf
import random
import time
from typing import Callable, Iterable, List, Optional

import requests
from requests.adapters import HTTPAdapter

try:  # urllib3 v1/v2 compatibility
    from urllib3.util.retry import Retry
except Exception:  # pragma: no cover
    Retry = None  # type: ignore

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

DEFAULT_TIMEOUT = 15


def build_session(timeout: int = DEFAULT_TIMEOUT) -> requests.Session:
    """Create a configured requests Session with retry/backoff."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/json,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    if Retry is not None:
        retry = Retry(
            total=2,
            backoff_factor=0.4,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "HEAD"]),
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=32, pool_maxsize=32)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
    session.request_timeout = timeout  # type: ignore[attr-defined]
    return session


def get(session: requests.Session, url: str, **kwargs) -> Optional[requests.Response]:
    """GET wrapper that never raises; returns None on failure."""
    timeout = kwargs.pop("timeout", getattr(session, "request_timeout", DEFAULT_TIMEOUT))
    try:
        return session.get(url, timeout=timeout, **kwargs)
    except requests.RequestException:
        return None


def run_concurrent(func: Callable, items: Iterable, max_workers: int = 20) -> List:
    """Run *func* over *items* concurrently, returning collected results."""
    results: List = []
    items = list(items)
    if not items:
        return results
    with cf.ThreadPoolExecutor(max_workers=min(max_workers, len(items))) as pool:
        futures = {pool.submit(func, it): it for it in items}
        for fut in cf.as_completed(futures):
            try:
                res = fut.result()
            except Exception:  # noqa: BLE001 - keep scanning resilient
                res = None
            if res is not None:
                results.append(res)
    return results
