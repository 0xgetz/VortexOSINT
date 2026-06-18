"""IP address intelligence — geolocation, ASN/ISP, reverse DNS and basic
threat hints, all via free keyless APIs (ip-api.com).
"""
from __future__ import annotations

import socket
from typing import Dict

from ..core import console, http


def _geolocate(ip: str, session) -> Dict:
    fields = "status,message,continent,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
    url = f"http://ip-api.com/json/{ip}?fields={fields}"
    resp = http.get(session, url)
    if resp is None:
        return {}
    try:
        data = resp.json()
    except Exception:  # noqa: BLE001
        return {}
    if data.get("status") != "success":
        return {"error": data.get("message", "lookup failed")}
    return data


def _reverse_dns(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:  # noqa: BLE001
        return ""


def investigate(ip: str, timeout: int = 15) -> Dict:
    console.section(f"IP scan: {ip}")
    session = http.build_session(timeout=timeout)

    console.info("Geolocating & resolving network owner...")
    geo = _geolocate(ip, session)
    rdns = _reverse_dns(ip) or geo.get("reverse", "")

    if geo and "error" not in geo:
        console.kv_panel("Location", {
            "IP": geo.get("query"),
            "Continent": geo.get("continent"),
            "Country": f"{geo.get('country')} ({geo.get('countryCode')})",
            "Region": geo.get("regionName"),
            "City": geo.get("city"),
            "ZIP": geo.get("zip"),
            "Coordinates": f"{geo.get('lat')}, {geo.get('lon')}",
            "Timezone": geo.get("timezone"),
            "Map": f"https://www.openstreetmap.org/?mlat={geo.get('lat')}&mlon={geo.get('lon')}#map=12/{geo.get('lat')}/{geo.get('lon')}"
            if geo.get("lat") else None,
        })
        console.kv_panel("Network", {
            "ISP": geo.get("isp"),
            "Organization": geo.get("org"),
            "ASN": geo.get("as"),
            "AS name": geo.get("asname"),
            "Reverse DNS": rdns,
        })
        console.kv_panel("Flags", {
            "Mobile network": geo.get("mobile"),
            "Proxy/VPN/Tor": geo.get("proxy"),
            "Hosting/Datacenter": geo.get("hosting"),
        })
    else:
        console.error(f"Lookup failed: {geo.get('error', 'unknown error') if geo else 'no response'}")

    return {"ip": ip, "geolocation": geo, "reverse_dns": rdns}
