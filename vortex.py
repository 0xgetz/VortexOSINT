#!/usr/bin/env python3
"""VortexOSINT launcher — run with `python vortex.py <command>`."""
import sys

from vortexosint.cli import main

if __name__ == "__main__":
    sys.exit(main())
