"""Image metadata (EXIF) extraction — camera info, timestamps and GPS
coordinates with a map link. Fully offline, uses Pillow.
"""
from __future__ import annotations

import os
from typing import Dict, Optional, Tuple

from ..core import console


def _to_decimal(dms, ref) -> Optional[float]:
    try:
        deg = float(dms[0]); minute = float(dms[1]); sec = float(dms[2])
        dec = deg + minute / 60.0 + sec / 3600.0
        if ref in ("S", "W"):
            dec = -dec
        return round(dec, 6)
    except Exception:  # noqa: BLE001
        return None


def _extract_gps(gps_ifd) -> Dict:
    from PIL.ExifTags import GPSTAGS

    gps = {GPSTAGS.get(k, k): v for k, v in gps_ifd.items()}
    lat = _to_decimal(gps.get("GPSLatitude"), gps.get("GPSLatitudeRef")) if gps.get("GPSLatitude") else None
    lon = _to_decimal(gps.get("GPSLongitude"), gps.get("GPSLongitudeRef")) if gps.get("GPSLongitude") else None
    out: Dict = {}
    if lat is not None and lon is not None:
        out["latitude"] = lat
        out["longitude"] = lon
        out["maps"] = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}"
        out["google_maps"] = f"https://maps.google.com/?q={lat},{lon}"
    if gps.get("GPSAltitude") is not None:
        try:
            out["altitude_m"] = round(float(gps["GPSAltitude"]), 2)
        except Exception:  # noqa: BLE001
            pass
    return out


def investigate(path: str) -> Dict:
    console.section(f"Image EXIF scan: {os.path.basename(path)}")
    if not os.path.isfile(path):
        console.error(f"File not found: {path}")
        return {"path": path, "available": False, "error": "file not found"}

    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
    except Exception:
        console.error("Pillow is required: pip install pillow")
        return {"path": path, "available": False, "error": "pillow not installed"}

    try:
        img = Image.open(path)
    except Exception as exc:  # noqa: BLE001
        console.error(f"Cannot open image: {exc}")
        return {"path": path, "available": False, "error": str(exc)}

    basics = {
        "Format": img.format,
        "Mode": img.mode,
        "Size": f"{img.size[0]}x{img.size[1]}px",
        "File size": f"{os.path.getsize(path) / 1024:.1f} KB",
    }
    console.kv_panel("Image", basics)

    exif = None
    try:
        exif = img._getexif()  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        exif = None

    if not exif:
        console.warn("No EXIF metadata embedded (image may be stripped or PNG/WebP).")
        return {"path": path, "available": True, "image": basics, "exif": {}, "gps": {}}

    tags: Dict = {}
    gps_data: Dict = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "GPSInfo" and isinstance(value, dict):
            gps_data = _extract_gps(value)
            continue
        if isinstance(value, bytes):
            value = value.decode(errors="replace")
        tags[str(tag)] = str(value)[:200]

    interesting = {k: tags[k] for k in (
        "Make", "Model", "Software", "DateTime", "DateTimeOriginal",
        "LensModel", "ExposureTime", "FNumber", "ISOSpeedRatings",
        "FocalLength", "Orientation", "Artist", "Copyright") if k in tags}
    if interesting:
        console.kv_panel("Camera / Capture", interesting)

    if gps_data:
        console.kv_panel("\U0001F4CD GPS Location", gps_data)
        console.success("GPS coordinates found — location can be mapped!")
    else:
        console.info("No GPS coordinates embedded.")

    return {"path": path, "available": True, "image": basics,
            "exif": tags, "gps": gps_data}
