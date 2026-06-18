"""Phone number OSINT — parsing, validation, carrier, region and timezone
using the offline `phonenumbers` library (Google libphonenumber). Fully free
and works without any network calls.
"""
from __future__ import annotations

from typing import Dict

from ..core import console


def investigate(number: str, default_region: str | None = None) -> Dict:
    console.section(f"Phone scan: {number}")
    try:
        import phonenumbers
        from phonenumbers import carrier, geocoder, timezone as pn_timezone
    except Exception:
        console.error("The 'phonenumbers' package is required. Install: pip install phonenumbers")
        return {"number": number, "available": False}

    try:
        parsed = phonenumbers.parse(number, default_region)
    except phonenumbers.NumberParseException as exc:
        console.error(f"Could not parse number: {exc}")
        return {"number": number, "valid": False, "error": str(exc)}

    is_valid = phonenumbers.is_valid_number(parsed)
    is_possible = phonenumbers.is_possible_number(parsed)

    number_type = {
        0: "Fixed line", 1: "Mobile", 2: "Fixed line or mobile", 3: "Toll free",
        4: "Premium rate", 5: "Shared cost", 6: "VoIP", 7: "Personal number",
        8: "Pager", 9: "UAN", 10: "Voicemail", 27: "Unknown",
    }.get(phonenumbers.number_type(parsed), "Unknown")

    result = {
        "number": number,
        "valid": is_valid,
        "possible": is_possible,
        "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
        "international": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
        "national": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
        "country_code": parsed.country_code,
        "region": geocoder.description_for_number(parsed, "en"),
        "carrier": carrier.name_for_number(parsed, "en"),
        "timezones": list(pn_timezone.time_zones_for_number(parsed)),
        "line_type": number_type,
    }

    console.kv_panel("Phone", {
        "Input": result["number"],
        "Valid": result["valid"],
        "E.164": result["e164"],
        "International": result["international"],
        "National": result["national"],
        "Country code": f"+{result['country_code']}",
        "Region": result["region"],
        "Carrier": result["carrier"],
        "Line type": result["line_type"],
        "Timezone(s)": ", ".join(result["timezones"]),
    })
    return result
