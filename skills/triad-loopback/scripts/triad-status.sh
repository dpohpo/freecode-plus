#!/usr/bin/env bash
set -euo pipefail

EVENTS="${XDG_STATE_HOME:-$HOME/.local/state}/triad-loopback/events.jsonl"
if [[ ! -f "$EVENTS" ]]; then
  echo "(no triad-loopback events yet)"
  exit 0
fi

tail -20 "$EVENTS"
