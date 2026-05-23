#!/usr/bin/env python3
"""Deprecated yqhsq hcom launcher stub.

yqhsq now uses Free Code's official Agent Teams flow:
TeamCreate -> Agent(name, team_name, prompt) -> SendMessage.
"""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "yqhsq legacy hcom launcher is disabled. "
        "Use Free Code Agent Teams: TeamCreate + Agent(name, team_name, prompt).",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
