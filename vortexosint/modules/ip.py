"""High-accuracy IP intelligence.

Accuracy strategy: query **three** independent free, keyless geolocation
providers (ip-api.com, ipwho.is, ipapi.co) concurrently, then build a
consensus. Fields agreed on by a majority are reported with a confidence
score; coordinates are averaged across agreeing providers. Reverse DNS and
network-owner (ASN/ISP) data are cross-checked too.
"""
from __future__ import annotations

import socket
from collections import Counter
from statistics import mean
from typing import Dict, List, Optional

from ..core import console, http


def _ip_api(ip, session) -> Optional[Dict]:
    fields = "status,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,proxy,hosting,mobile,reverse,query"
    r = http.get(session, f"http://ip-api.com/json/{ip}?fields={fields}")
    if r is None:
        return None
    try:
        d = r.json()
    except Exception:  # noqa: BLE001
        return None
    if d.get("status") != "success":
        return None
    return {"provider": "ip-api.com", "country": d.get("country"), "country_code": d.get("countryCode"),
            "region": d.get("regionName"), "city": d.get("city"), "zip": d.get("zip"),
            "lat": d.get("lat"), "lon": d.get("lon"), "timezone": d.get("timezone"),
            "isp": d.get("isp"), "org": d.get("org"), "asn": d.get("as"),
            "proxy": d.get("proxy"), "hosting": d.get("hosting"), "mobile": d.get("mobile")}


def _ipwho(ip, session) -> Optional[Dict]:
    r = http.get(session, f"https://ipwho.is/{ip}")
    if r is None:
        return None
    try:
        d = r.json()
    except Exception:  # noqa: BLE001
        return None
    if not d.get("success", False):
        return None
    conn = d.get("connection", {}) or {}
    return {"provider": "ipwho.is", "country": d.get("country"), "country_code": d.get("country_code"),
            "region": d.get("region"), "city": d.get("city"), "zip": d.get("postal"),
            "lat": d.get("latitude"), "lon": d.get("longitude"),
            "timezone": (d.get("timezone") or {}).get("id"),
            "isp": conn.get("isp"), "org": conn.get("org"),
            "asn": f"AS{conn.get('asn')}" if conn.get("asn") else None}


def _ipapi(ip, session) -> Optional[Dict]:
    r = http.get(session, f"https://ipapi.co/{ip}/json/")
    if r is None:
        return None
    try:
        d = r.json()
    except Exception:  # noqa: BLE001
        return None
    if d.get("error"):
        return None
    return {"provider": "ipapi.co", "country": d.get("country_name"), "country_code": d.get("country_code"),
            "region": d.get("region"), "city": d.get("city"), "zip": d.get("postal"),
            "lat": d.get("latitude"), "lon": d.get("longitude"), "timezone": d.get("timezone"),
            "isp": d.get("org"), "org": d.get("org"), "asn": d.get("asn")}


def _reverse_dns(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:  # noqa: BLE001
        return ""


def _consensus(values: List, numeric: bool = False):
    vals = [v for v in values if v not in (None, "", "Unknown")]
    if not vals:
        return None, 0.0
    if numeric:
        try:
            nums = [float(v) for v in vals]
            # agreement = providers within ~0.5 deg of the mean
            m = mean(nums)
            agree = [n for n in nums if abs(n - m) <= 0.5]
            return round(mean(agree) if agree else m, 6), len(agree) / len(values)
        except Exception:  # noqa: BLE001
            return vals[0], 0.0
    counts = Counter(str(v).strip() for v in vals)
    top, n = counts.most_common(1)[0]
    return top, n / len(values)


def investigate(ip: str, timeout: int = 15) -> Dict:
    console.section(f"IP scan: {ip}")
    session = http.build_session(timeout=timeout)

    console.info("Querying 3 geolocation providers for consensus...")
    providers = [p for p in http.run_concurrent(
        lambda fn: fn(ip, session), [_ip_api, _ipwho, _ipapi], max_workers=3) if p]
    n = len(providers)
    rdns = _reverse_dns(ip)

    if n == 0:
        console.error("All providers failed to resolve this IP.")
        return {"ip": ip, "providers": 0, "reverse_dns": rdns}

    def field(key, numeric=False):
        return _consensus([p.get(key) for p in providers], numeric=numeric)

    country, c_conf = field("country")
    cc, _ = field("country_code")
    region, r_conf = field("region")
    city, city_conf = field("city")
    zipc, _ = field("zip")
    lat, lat_conf = field("lat", numeric=True)
    lon, lon_conf = field("lon", numeric=True)
    tz, _ = field("timezone")
    isp, isp_conf = field("isp")
    asn, asn_conf = field("asn")

    def pct(x):
        return f"{int(round(x * 100))}%"

    console.kv_panel("Location (consensus)", {
        "IP": ip,
        "Country": f"{country} ({cc})  [{pct(c_conf)} agree]",
        "Region": f"{region}  [{pct(r_conf)} agree]" if region else None,
        "City": f"{city}  [{pct(city_conf)} agree]" if city else None,
        "ZIP": zipc,
        "Coordinates": f"{lat}, {lon}  [{pct((lat_conf + lon_conf) / 2)} agree]" if lat else None,
        "Timezone": tz,
        "Map": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=12/{lat}/{lon}" if lat else None,
    })
    console.kv_panel("Network", {
        "ISP": f"{isp}  [{pct(isp_conf)} agree]" if isp else None,
        "ASN": f"{asn}  [{pct(asn_conf)} agree]" if asn else None,
        "Reverse DNS": rdns,
    })

    # Threat flags only ip-api provides reliably
    flags = next((p for p in providers if p["provider"] == "ip-api.com"), {})
    console.kv_panel("Flags", {
        "Proxy/VPN/Tor": flags.get("proxy"),
        "Hosting/Datacenter": flags.get("hosting"),
        "Mobile network": flags.get("mobile"),
    })

    overall = round(mean([c_conf, city_conf, (lat_conf + lon_conf) / 2]) * 100)
    console.success(f"Consensus from {n}/3 providers · overall location confidence ~{overall}%")

    return {
        "ip": ip,
        "providers": n,
        "consensus": {
            "country": country, "country_code": cc, "region": region, "city": city,
            "zip": zipc, "latitude": lat, "longitude": lon, "timezone": tz,
            "isp": isp, "asn": asn,
        },
        "confidence": {
            "country": round(c_conf, 2), "city": round(city_conf, 2),
            "coordinates": round((lat_conf + lon_conf) / 2, 2), "overall_pct": overall,
        },
        "flags": {"proxy": flags.get("proxy"), "hosting": flags.get("hosting"), "mobile": flags.get("mobile")},
        "reverse_dns": rdns,
        "raw_providers": providers,
    }
