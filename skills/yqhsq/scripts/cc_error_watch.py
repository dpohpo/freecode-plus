#!/usr/bin/env python3
"""Continuously harvest yqhsq/cc errors into a durable ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TRIGGER_RE = re.compile(
    r"running stop hooks|error|exception|traceback|failed|panic|fatal|❌|timeout|timed out|denied|forbidden|not found|missing",
    re.IGNORECASE,
)
CATEGORY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("stop_hook_blocked", re.compile(r"running stop hooks|stop hook", re.IGNORECASE)),
    ("timeout", re.compile(r"timeout|timed out|deadline exceeded", re.IGNORECASE)),
    ("permission_denied", re.compile(r"permission denied|forbidden|not allowed|eacces|eperm", re.IGNORECASE)),
    ("missing_dependency", re.compile(r"not found|missing|no such file|module not found|missing skill", re.IGNORECASE)),
    ("python_exception", re.compile(r"traceback|exception|module[nN]ot[fF]ound|keyerror|valueerror|typeerror", re.IGNORECASE)),
    ("browser_control", re.compile(r"chrome|websocket|debug port|tab-open|tab-focus|dom state", re.IGNORECASE)),
    ("codex_control", re.compile(r"codex", re.IGNORECASE)),
    ("generic_error", re.compile(r"error|failed|panic|fatal|❌", re.IGNORECASE)),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watch yqhsq panes and record errors.")
    parser.add_argument("--window-name", default="五神")
    parser.add_argument("--interval", type=float, default=20.0)
    parser.add_argument("--tail-lines", type=int, default=250)
    parser.add_argument("--jsonl-path", default=str(Path.home() / ".brain" / "shared_memory" / "recent" / "cc_error_ledger.jsonl"))
    parser.add_argument("--markdown-path", default=str(Path.home() / ".brain" / "shared_memory" / "recent" / "cc_error_ledger.md"))
    parser.add_argument("--state-file", default=str(Path.home() / ".brain" / "yqhsq" / "cc_error_watch_state.json"))
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_tmux(*args: str) -> str:
    completed = subprocess.run(["tmux", *args], check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        return ""
    return completed.stdout


def find_window_target(window_name: str) -> str | None:
    output = run_tmux("list-windows", "-a", "-F", "#{session_name}:#{window_index}\t#{window_name}")
    for line in output.splitlines():
        target, listed_name = (line.split("\t", 1) + [""])[:2]
        if listed_name == window_name:
            return target
    return None


def list_panes(window_target: str) -> list[dict[str, str]]:
    output = run_tmux("list-panes", "-t", window_target, "-F", "#{pane_id}\t#{pane_index}\t#{pane_title}")
    panes: list[dict[str, str]] = []
    for line in output.splitlines():
        pane_id, pane_index, pane_title = (line.split("\t", 2) + ["", ""])[:3]
        panes.append({"pane_id": pane_id, "pane_index": pane_index, "pane_title": pane_title})
    return panes


def capture_pane(pane_id: str, tail_lines: int) -> str:
    return run_tmux("capture-pane", "-p", "-t", pane_id, "-S", f"-{tail_lines}")


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"seen_hashes": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"seen_hashes": []}


def save_state(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def classify_error(line: str) -> str:
    for category, pattern in CATEGORY_PATTERNS:
        if pattern.search(line):
            return category
    return "generic_error"


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def load_recent_events(path: Path, limit: int = 80) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    events: list[dict[str, Any]] = []
    for raw in lines[-limit:]:
        try:
            events.append(json.loads(raw))
        except Exception:
            continue
    return events


def write_markdown_summary(path: Path, events: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter(event.get("category", "unknown") for event in events)
    lines = [
        "# CC Error Ledger",
        "",
        f"- Updated: `{now_iso()}`",
        f"- Total recent events: `{len(events)}`",
        "",
        "## Categories",
        "",
    ]
    for category, count in counts.most_common():
        lines.append(f"- `{category}`: {count}")
    lines.extend(["", "## Recent Events", ""])
    for event in events[-20:]:
        lines.append(
            f"- `{event.get('ts')}` [{event.get('category')}] pane {event.get('pane_index')} `{event.get('pane_title')}`: {event.get('line')}"
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def scan_once(*, window_name: str, tail_lines: int, state: dict[str, Any], jsonl_path: Path, markdown_path: Path) -> dict[str, Any]:
    window_target = find_window_target(window_name)
    if not window_target:
        return {"status": "window_missing", "new_events": 0}

    seen_hashes = list(state.get("seen_hashes", []))
    seen_hash_set = set(seen_hashes)
    new_events: list[dict[str, Any]] = []

    for pane in list_panes(window_target):
        content = capture_pane(pane["pane_id"], tail_lines)
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or not TRIGGER_RE.search(line):
                continue
            signature = hashlib.sha1(f"{pane['pane_id']}::{line}".encode("utf-8")).hexdigest()
            if signature in seen_hash_set:
                continue
            seen_hash_set.add(signature)
            seen_hashes.append(signature)
            event = {
                "ts": now_iso(),
                "window_target": window_target,
                "pane_id": pane["pane_id"],
                "pane_index": pane["pane_index"],
                "pane_title": pane["pane_title"],
                "category": classify_error(line),
                "line": line,
            }
            append_event(jsonl_path, event)
            new_events.append(event)

    state["seen_hashes"] = seen_hashes[-2000:]
    recent_events = load_recent_events(jsonl_path)
    write_markdown_summary(markdown_path, recent_events)
    return {"status": "ok", "new_events": len(new_events)}


def main() -> int:
    args = parse_args()
    jsonl_path = Path(args.jsonl_path)
    markdown_path = Path(args.markdown_path)
    state_file = Path(args.state_file)

    while True:
        state = load_state(state_file)
        result = scan_once(
            window_name=args.window_name,
            tail_lines=args.tail_lines,
            state=state,
            jsonl_path=jsonl_path,
            markdown_path=markdown_path,
        )
        state["last_scan_at"] = now_iso()
        state["last_result"] = result
        save_state(state_file, state)
        if args.once:
            print(json.dumps(result, ensure_ascii=False))
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
