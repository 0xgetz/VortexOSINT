"""Domain reconnaissance — WHOIS, DNS records, subdomain discovery (crt.sh),
HTTP headers and technology hints. All from free, public sources.
"""
from __future__ import annotations

from typing import Dict, List

from ..core import console, http


def _whois(domain: str) -> Dict:
    try:
        import whois  # python-whois
    except Exception:
        return {"available": False, "note": "python-whois not installed"}
    try:
        w = whois.whois(domain)

        def first(val):
            return val[0] if isinstance(val, list) and val else val

        return {
            "available": True,
            "registrar": w.registrar,
            "created": str(first(w.creation_date)) if w.creation_date else None,
            "expires": str(first(w.expiration_date)) if w.expiration_date else None,
            "updated": str(first(w.updated_date)) if w.updated_date else None,
            "name_servers": sorted({n.lower() for n in (w.name_servers or [])}) if w.name_servers else [],
            "emails": w.emails if isinstance(w.emails, list) else ([w.emails] if w.emails else []),
            "org": w.org,
            "country": w.country,
        }
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": str(exc)}


def _dns(domain: str) -> Dict:
    try:
        import dns.resolver  # dnspython
    except Exception:
        return {"available": False, "note": "dnspython not installed"}
    records: Dict[str, List[str]] = {}
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 6.0
    for rtype in ("A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"):
        try:
            answers = resolver.resolve(domain, rtype)
            records[rtype] = [r.to_text() for r in answers]
        except Exception:  # noqa: BLE001
            continue
    return {"available": True, "records": records}


def _subdomains(domain: str, session) -> List[str]:
    """Passive subdomain enumeration via the free crt.sh certificate log."""
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    resp = http.get(session, url, timeout=25)
    subs = set()
    if resp is not None and resp.status_code == 200:
        try:
            for entry in resp.json():
                for name in str(entry.get("name_value", "")).splitlines():
                    name = name.strip().lstrip("*.").lower()
                    if name.endswith(domain) and "@" not in name:
                        subs.add(name)
        except Exception:  # noqa: BLE001
            pass
    return sorted(subs)


def _http_headers(domain: str, session) -> Dict:
    for scheme in ("https", "http"):
        resp = http.get(session, f"{scheme}://{domain}", allow_redirects=True)
        if resp is not None:
            interesting = ("server", "x-powered-by", "via", "cf-ray",
                           "x-frame-options", "strict-transport-security",
                           "content-security-policy")
            headers = {k: v for k, v in resp.headers.items() if k.lower() in interesting}
            return {"final_url": resp.url, "status": resp.status_code, "headers": headers}
    return {}


def investigate(domain: str, timeout: int = 15, deep: bool = True) -> Dict:
    domain = domain.lower().strip().replace("https://", "").replace("http://", "").strip("/")
    console.section(f"Domain scan: {domain}")
    session = http.build_session(timeout=timeout)

    console.info("Resolving WHOIS registration...")
    whois_data = _whois(domain)
    console.kv_panel("WHOIS", {k: v for k, v in whois_data.items() if k != "available"})

    console.info("Querying DNS records...")
    dns_data = _dns(domain)
    if dns_data.get("records"):
        rows = [[t, ", ".join(v)] for t, v in dns_data["records"].items()]
        console.results_table("DNS records", ["Type", "Values"], rows)

    console.info("HTTP fingerprint...")
    http_data = _http_headers(domain, session)
    if http_data:
        console.kv_panel("HTTP", {"Final URL": http_data.get("final_url"),
                                  "Status": http_data.get("status"),
                                  **http_data.get("headers", {})})

    subs: List[str] = []
    if deep:
        console.info("Enumerating subdomains via crt.sh (passive)...")
        subs = _subdomains(domain, session)
        if subs:
            console.results_table(f"Subdomains ({len(subs)})", ["Subdomain"], [[s] for s in subs])
        else:
            console.warn("No subdomains discovered via certificate transparency.")

    return {
        "domain": domain,
        "whois": whois_data,
        "dns": dns_data.get("records", {}),
        "http": http_data,
        "subdomains": subs,
        "subdomain_count": len(subs),
    }
