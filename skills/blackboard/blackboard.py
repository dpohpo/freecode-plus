#!/usr/bin/env python3
"""Blackboard — file-based task board for multi-agent coordination.

Design:
  - Single JSON file as shared blackboard (no DB, no server)
  - Agents read board, claim tasks, update status
  - DAG dependencies with blocked detection
  - Atomic file writes (write-tmp + rename)

Distilled from vibe-kanban (24k stars) + agent-kanban (140 stars).
"""

import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Default board location ──────────────────────────────────────────
DEFAULT_BOARD = os.environ.get("BLACKBOARD_FILE", ".blackboard/board.json")

# ── Status enum ─────────────────────────────────────────────────────
STATUSES = ("todo", "claimed", "in_progress", "in_review", "done", "cancelled")

# ── State machine: {action: (allowed_from, target, allowed_roles)} ──
TRANSITIONS = {
    "claim":    (["todo"],                    "claimed",     ["agent"]),
    "start":    (["claimed"],                 "in_progress", ["agent"]),
    "review":   (["in_progress"],             "in_review",   ["agent"]),
    "complete": (["in_review"],               "done",        ["lead", "critic"]),
    "reject":   (["in_review"],               "in_progress", ["lead", "critic"]),
    "cancel":   (["todo","claimed","in_progress","in_review"], "cancelled", ["lead"]),
    "release":  (["claimed","in_progress"],   "todo",        ["lead", "agent"]),
}

# ── Board I/O ───────────────────────────────────────────────────────

def _board_path(path: Optional[str] = None) -> Path:
    return Path(path or DEFAULT_BOARD)


def load_board(path: Optional[str] = None) -> dict:
    p = _board_path(path)
    if not p.exists():
        return {"tasks": [], "log": [], "meta": {"created": _now()}}
    return json.loads(p.read_text())


def save_board(board: dict, path: Optional[str] = None):
    p = _board_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(board, ensure_ascii=False, indent=2))
    tmp.rename(p)  # atomic on POSIX


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _short_id() -> str:
    return uuid.uuid4().hex[:8]


def _log(board: dict, action: str, task_id: str, agent: str = "", detail: str = ""):
    board["log"].append({
        "ts": _now(), "action": action, "task_id": task_id,
        "agent": agent, "detail": detail
    })


def _find_task(board: dict, task_id: str) -> Optional[dict]:
    for t in board["tasks"]:
        if t["id"] == task_id:
            return t
    return None


# ── Blocked detection (DAG) ─────────────────────────────────────────

def _is_blocked(board: dict, task: dict) -> bool:
    """A task is blocked if any of its deps are not 'done'."""
    deps = task.get("depends_on", [])
    if not deps:
        return False
    for dep_id in deps:
        dep = _find_task(board, dep_id)
        if dep is None or dep["status"] != "done":
            return True
    return False


# ── Commands ────────────────────────────────────────────────────────

def cmd_init(args):
    """Initialize a new blackboard."""
    board = load_board(args.board)
    if board["tasks"]:
        print(f"Board already exists with {len(board['tasks'])} tasks.")
        return
    save_board(board, args.board)
    print(f"Blackboard initialized at {_board_path(args.board)}")


def cmd_add(args):
    """Add a task to the board."""
    board = load_board(args.board)
    task = {
        "id": _short_id(),
        "title": args.title,
        "description": args.description or "",
        "status": "todo",
        "owner": "",
        "priority": args.priority or "normal",
        "labels": args.labels.split(",") if args.labels else [],
        "depends_on": args.depends.split(",") if args.depends else [],
        "created_at": _now(),
        "updated_at": _now(),
    }
    board["tasks"].append(task)
    _log(board, "add", task["id"], detail=task["title"])
    save_board(board, args.board)
    print(f"+ [{task['id']}] {task['title']}")


def cmd_list(args):
    """List tasks on the board."""
    board = load_board(args.board)
    if not board["tasks"]:
        print("(empty board)")
        return

    # Filter
    tasks = board["tasks"]
    if args.status:
        tasks = [t for t in tasks if t["status"] == args.status]
    if args.agent:
        tasks = [t for t in tasks if t["owner"] == args.agent]
    if args.available:
        tasks = [t for t in tasks if t["status"] == "todo" and not _is_blocked(board, t)]

    # Group by status
    grouped = {}
    for t in tasks:
        grouped.setdefault(t["status"], []).append(t)

    for status in STATUSES:
        items = grouped.get(status, [])
        if not items:
            continue
        print(f"\n{'─'*3} {status.upper()} ({len(items)}) {'─'*40}")
        for t in items:
            blocked = " [BLOCKED]" if _is_blocked(board, t) else ""
            owner = f" @{t['owner']}" if t["owner"] else ""
            pri = f" !{t['priority']}" if t["priority"] != "normal" else ""
            deps = f" deps:{','.join(t['depends_on'])}" if t.get("depends_on") else ""
            print(f"  [{t['id']}]{pri}{owner}{blocked}{deps} {t['title']}")
    print()


def cmd_claim(args):
    """Agent claims an available task."""
    board = load_board(args.board)
    task = _find_task(board, args.task_id)
    if not task:
        print(f"Task {args.task_id} not found"); sys.exit(1)
    if task["status"] != "todo":
        print(f"Cannot claim: status is '{task['status']}'"); sys.exit(1)
    if _is_blocked(board, task):
        print(f"Cannot claim: task is blocked by deps"); sys.exit(1)
    if task["owner"]:
        print(f"Already claimed by @{task['owner']}"); sys.exit(1)

    task["status"] = "claimed"
    task["owner"] = args.agent
    task["updated_at"] = _now()
    _log(board, "claim", task["id"], args.agent)
    save_board(board, args.board)
    print(f"Claimed [{task['id']}] → @{args.agent}")


def cmd_update(args):
    """Transition task status."""
    board = load_board(args.board)
    task = _find_task(board, args.task_id)
    if not task:
        print(f"Task {args.task_id} not found"); sys.exit(1)

    action = args.action
    if action not in TRANSITIONS:
        print(f"Unknown action: {action}. Valid: {list(TRANSITIONS.keys())}"); sys.exit(1)

    allowed_from, target, _ = TRANSITIONS[action]
    if task["status"] not in allowed_from:
        print(f"Cannot '{action}': current status '{task['status']}', need {allowed_from}"); sys.exit(1)

    task["status"] = target
    task["updated_at"] = _now()
    if action == "release":
        task["owner"] = ""
    if args.note:
        task["result"] = args.note
    _log(board, action, task["id"], args.agent or task["owner"], args.note or "")
    save_board(board, args.board)
    print(f"[{task['id']}] {action} → {target}")


def cmd_next(args):
    """Recommend next task for an agent (blackboard pull)."""
    board = load_board(args.board)
    available = [
        t for t in board["tasks"]
        if t["status"] == "todo" and not t["owner"] and not _is_blocked(board, t)
    ]
    if not available:
        print("No available tasks.")
        return

    # Sort: high > normal > low, then by creation time
    pri_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
    available.sort(key=lambda t: (pri_order.get(t["priority"], 2), t["created_at"]))

    # If agent specified, prefer tasks matching agent labels
    pick = available[0]
    print(f"Recommended: [{pick['id']}] {pick['title']} (priority: {pick['priority']})")
    return pick


def cmd_info(args):
    """Show task details."""
    board = load_board(args.board)
    task = _find_task(board, args.task_id)
    if not task:
        print(f"Task {args.task_id} not found"); sys.exit(1)

    blocked = _is_blocked(board, task)
    print(f"ID:          {task['id']}")
    print(f"Title:       {task['title']}")
    print(f"Status:      {task['status']}{' [BLOCKED]' if blocked else ''}")
    print(f"Owner:       {task['owner'] or '(unassigned)'}")
    print(f"Priority:    {task['priority']}")
    print(f"Labels:      {', '.join(task['labels']) or '(none)'}")
    print(f"Depends on:  {', '.join(task['depends_on']) or '(none)'}")
    print(f"Description: {task['description'] or '(none)'}")
    if task.get("result"):
        print(f"Result:      {task['result']}")
    print(f"Created:     {task['created_at']}")
    print(f"Updated:     {task['updated_at']}")

    # Show related log entries
    logs = [l for l in board["log"] if l["task_id"] == task["id"]]
    if logs:
        print(f"\n--- History ---")
        for l in logs[-10:]:
            agent = f" @{l['agent']}" if l["agent"] else ""
            detail = f" | {l['detail']}" if l["detail"] else ""
            print(f"  {l['ts']} {l['action']}{agent}{detail}")


def cmd_log(args):
    """Show board activity log."""
    board = load_board(args.board)
    logs = board["log"]
    if args.tail:
        logs = logs[-int(args.tail):]
    for l in logs:
        agent = f" @{l['agent']}" if l["agent"] else ""
        detail = f" | {l['detail']}" if l["detail"] else ""
        print(f"{l['ts']} [{l['task_id']}] {l['action']}{agent}{detail}")


def cmd_summary(args):
    """Print board summary (for agents to quickly read the blackboard)."""
    board = load_board(args.board)
    tasks = board["tasks"]
    if not tasks:
        print("(empty board)"); return

    counts = {}
    for t in tasks:
        counts[t["status"]] = counts.get(t["status"], 0) + 1

    total = len(tasks)
    blocked = sum(1 for t in tasks if _is_blocked(board, t))
    available = sum(1 for t in tasks if t["status"] == "todo" and not _is_blocked(board, t))

    print(f"Tasks: {total} total | Available: {available} | Blocked: {blocked}")
    for s in STATUSES:
        if s in counts:
            print(f"  {s}: {counts[s]}")

    # Show who's working on what
    owners = {}
    for t in tasks:
        if t["owner"] and t["status"] not in ("done", "cancelled"):
            owners.setdefault(t["owner"], []).append(t)
    if owners:
        print("\nActive agents:")
        for agent, agent_tasks in owners.items():
            task_strs = [f"[{t['id']}] {t['title']}" for t in agent_tasks]
            print(f"  @{agent}: {'; '.join(task_strs)}")


# ── CLI ─────────────────────────────────────────────────────────────

def main():
    import argparse
    p = argparse.ArgumentParser(prog="blackboard", description="File-based task board for multi-agent coordination")
    p.add_argument("--board", "-b", default=DEFAULT_BOARD, help="Board file path")

    sub = p.add_subparsers(dest="cmd")

    # init
    sub.add_parser("init", help="Initialize board")

    # add
    a = sub.add_parser("add", help="Add task")
    a.add_argument("title")
    a.add_argument("--description", "-d")
    a.add_argument("--priority", "-p", choices=["critical","high","normal","low"])
    a.add_argument("--labels", "-l", help="Comma-separated labels")
    a.add_argument("--depends", help="Comma-separated task IDs")

    # list
    ls = sub.add_parser("list", help="List tasks")
    ls.add_argument("--status", "-s")
    ls.add_argument("--agent", "-a")
    ls.add_argument("--available", action="store_true", help="Show only claimable tasks")

    # claim
    c = sub.add_parser("claim", help="Claim a task")
    c.add_argument("task_id")
    c.add_argument("agent")

    # update
    u = sub.add_parser("update", help="Transition task status")
    u.add_argument("task_id")
    u.add_argument("action", choices=list(TRANSITIONS.keys()))
    u.add_argument("--agent", "-a")
    u.add_argument("--note", "-n")

    # next
    n = sub.add_parser("next", help="Recommend next task for agent")
    n.add_argument("--agent", "-a")

    # info
    i = sub.add_parser("info", help="Show task details")
    i.add_argument("task_id")

    # log
    lg = sub.add_parser("log", help="Show activity log")
    lg.add_argument("--tail", "-t", default="20")

    # summary
    sub.add_parser("summary", help="Board summary for agents")

    args = p.parse_args()
    if not args.cmd:
        p.print_help(); sys.exit(1)

    {
        "init": cmd_init, "add": cmd_add, "list": cmd_list,
        "claim": cmd_claim, "update": cmd_update, "next": cmd_next,
        "info": cmd_info, "log": cmd_log, "summary": cmd_summary,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
