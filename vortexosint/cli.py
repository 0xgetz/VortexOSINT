"""VortexOSINT command-line interface."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

from . import __version__
from .core import console, report
from .modules import domain as domain_mod
from .modules import email as email_mod
from .modules import ip as ip_mod
from .modules import phone as phone_mod
from .modules import username as username_mod

BANNER = r"""
 __     __        _            ___  ____ ___ _   _ _____
 \ \   / /__  _ _| |_ _____  _/ _ \/ ___|_ _| \ | |_   _|
  \ \ / / _ \| '_| __/ _ \ \/ / | | \___ \| ||  \| | | |
   \ V / (_) | | | ||  __/>  <| |_| |___) | || |\  | | |
    \_/ \___/|_|  \__\___/_/\_\\___/|____/___|_| \_| |_|
"""


def _export(args, target: str, scan_type: str, data: dict) -> None:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() else "_" for c in target)[:40]
    if args.json:
        path = args.json if isinstance(args.json, str) else f"vortex_{scan_type}_{safe}_{stamp}.json"
        console.success(f"JSON report saved: {report.to_json(data, path)}")
    if args.html:
        path = args.html if isinstance(args.html, str) else f"vortex_{scan_type}_{safe}_{stamp}.html"
        console.success(f"HTML report saved: {report.to_html(target, scan_type, data, path)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vortex",
        description="VortexOSINT — modern, complete, 100%% free OSINT toolkit.",
        epilog="Use only on targets you own or are authorized to investigate.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"VortexOSINT {__version__}")
    parser.add_argument("--no-banner", action="store_true", help="Hide the ASCII banner")

    sub = parser.add_subparsers(dest="command", metavar="<command>")

    common_out = argparse.ArgumentParser(add_help=False)
    common_out.add_argument("--json", nargs="?", const=True, help="Export JSON (optional path)")
    common_out.add_argument("--html", nargs="?", const=True, help="Export HTML report (optional path)")
    common_out.add_argument("--timeout", type=int, default=15, help="HTTP timeout seconds (default 15)")

    p_user = sub.add_parser("username", parents=[common_out], help="Find a username across 40+ sites")
    p_user.add_argument("username")
    p_user.add_argument("--workers", type=int, default=25, help="Concurrent workers")

    p_email = sub.add_parser("email", parents=[common_out], help="Investigate an email address")
    p_email.add_argument("email")

    p_domain = sub.add_parser("domain", parents=[common_out], help="Recon a domain")
    p_domain.add_argument("domain")
    p_domain.add_argument("--no-deep", action="store_true", help="Skip subdomain enumeration")

    p_ip = sub.add_parser("ip", parents=[common_out], help="Geolocate & profile an IP")
    p_ip.add_argument("ip")

    p_phone = sub.add_parser("phone", parents=[common_out], help="Parse & profile a phone number")
    p_phone.add_argument("number")
    p_phone.add_argument("--region", help="Default region code, e.g. US, ID, GB")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "no_banner", False):
        console.banner(BANNER)
        console.banner(f"        v{__version__} — 100% free OSINT toolkit\n")

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "username":
            data = username_mod.search(args.username, timeout=args.timeout, max_workers=args.workers)
            _export(args, args.username, "username", {"username_search": data})
        elif args.command == "email":
            data = email_mod.investigate(args.email, timeout=args.timeout)
            _export(args, args.email, "email", {"email": data})
        elif args.command == "domain":
            data = domain_mod.investigate(args.domain, timeout=args.timeout, deep=not args.no_deep)
            _export(args, args.domain, "domain", {"domain": data})
        elif args.command == "ip":
            data = ip_mod.investigate(args.ip, timeout=args.timeout)
            _export(args, args.ip, "ip", {"ip": data})
        elif args.command == "phone":
            data = phone_mod.investigate(args.number, default_region=args.region)
            _export(args, args.number, "phone", {"phone": data})
    except KeyboardInterrupt:
        console.warn("Interrupted by user.")
        return 130

    return 0


if __name__ == "__main__":
    sys.exit(main())
