#!/usr/bin/env python3
"""Keep the Codex web lane alive and maintain yqhsq health telemetry."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AGENT_ROLES: dict[str, str] = {
    "taiyi": "dispatcher",
    "yuanshi": "worker",
    "lingbao": "worker",
    "daode": "worker",
    "guanmiao": "worker",
    "siguo": "error_recorder",
    "xuanshu": "context_monitor",
}
AGENT_ORDER = list(AGENT_ROLES)
STATUS_CONTEXT_RE = re.compile(r"(\d{1,3})%")
STATUS_COST_RE = re.compile(r"\$([0-9]+(?:\.[0-9]+)?)")
STATUS_MODEL_RE = re.compile(r"(Opus(?:\s+[0-9.]+)?|Sonnet(?:\s+[0-9.]+)?|Haiku(?:\s+[0-9.]+)?)", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect Codex idleness and collect yqhsq health telemetry.")
    parser.add_argument("--brain-root", default="/Volumes/金阳/brain")
    parser.add_argument("--workspace", default="/Volumes/金阳/brain")
    parser.add_argument("--label", default="codex-login")
    parser.add_argument("--interval", type=float, default=300.0)
    parser.add_argument("--idle-threshold", type=float, default=300.0)
    parser.add_argument("--window-name", default="五神")
    parser.add_argument("--heavy-threshold", type=int, default=40)
    parser.add_argument("--critical-threshold", type=int, default=70)
    parser.add_argument("--snapshot-stale-seconds", type=float, default=900.0)
    parser.add_argument("--command-timeout", type=float, default=45.0)
    parser.add_argument("--snapshots-file", default=str(Path.home() / ".brain" / "shared_memory" / "recent" / "cc_statusline_snapshots.jsonl"))
    parser.add_argument("--health-file", default=str(Path.home() / ".brain" / "shared_memory" / "recent" / "cc_agent_health.json"))
    parser.add_argument("--health-log-file", default=str(Path.home() / ".brain" / "shared_memory" / "recent" / "cc_agent_health.jsonl"))
    parser.add_argument("--ccusage-script", default="/Volumes/金阳/brain/scripts/ccusage-blocks.sh")
    parser.add_argument("--codexbar-script", default="/Volumes/金阳/brain/scripts/codexbar-codex-usage.sh")
    parser.add_argument("--state-file", default=str(Path.home() / ".brain" / "shared_memory" / "recent" / "codex_detector_state.json"))
    parser.add_argument("--log-file", default=str(Path.home() / ".brain" / "shared_memory" / "recent" / "codex_detector_log.jsonl"))
    parser.add_argument("--controller-state", default=str(Path.home() / ".brain" / "codex_controller_state.json"))
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def now() -> datetime:
    return datetime.now(timezone.utc)


def now_iso() -> str:
    return now().isoformat()


def parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def run_cmd(args: list[str], *, cwd: str | None = None, timeout: float = 120.0) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout.decode("utf-8", "replace") if exc.stdout else "")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr.decode("utf-8", "replace") if exc.stderr else "")
        if not stderr:
            stderr = f"timed out after {timeout}s"
        return subprocess.CompletedProcess(args=args, returncode=124, stdout=stdout, stderr=stderr)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def registry_has_codex_label(label: str) -> bool:
    registry = load_json(Path.home() / ".brain" / "gui_tab_registry.json")
    entry = registry.get(label)
    return bool(entry and entry.get("target") == "codex-web")


def ensure_codex_tab(*, brain_root: str, label: str) -> None:
    if registry_has_codex_label(label):
        return
    run_cmd(
        [
            "uv",
            "run",
            "brain-gui-demo",
            "tab-open",
            "--target",
            "codex-web",
            "--label",
            label,
            "--purpose",
            "coding",
            "--topic",
            "codex",
        ],
        cwd=brain_root,
        timeout=90.0,
    )


def probe_codex_state(*, brain_root: str, label: str) -> dict[str, Any]:
    completed = run_cmd(["bash", f"{brain_root}/scripts/web-chat.sh", "state", label], cwd=brain_root, timeout=60.0)
    if completed.returncode != 0:
        return {
            "ok": False,
            "error": completed.stderr.strip() or completed.stdout.strip() or "state_probe_failed",
        }
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid_state_json", "raw": completed.stdout}
    dom_state = payload.get("dom_state", {})
    return {
        "ok": True,
        "generating": bool(dom_state.get("generating")),
        "input_ready": bool(dom_state.get("textInputs")),
        "url": payload.get("page", {}).get("url"),
        "title": payload.get("page", {}).get("title"),
        "payload": payload,
    }


def run_tmux(*args: str) -> str:
    completed = run_cmd(["tmux", *args], timeout=15.0)
    if completed.returncode != 0:
        return ""
    return completed.stdout


def find_window_target(window_name: str) -> str | None:
    output = run_tmux("list-windows", "-a", "-F", "#{session_name}:#{window_index}|#{window_name}")
    for raw_line in output.splitlines():
        target, listed_name = (raw_line.split("|", 1) + [""])[:2]
        if listed_name == window_name:
            return target
    return None


def list_window_panes(window_target: str) -> list[dict[str, str]]:
    output = run_tmux("list-panes", "-t", window_target, "-F", "#{pane_id}|#{pane_title}")
    panes: list[dict[str, str]] = []
    for raw_line in output.splitlines():
        pane_id, pane_title = (raw_line.split("|", 1) + [""])[:2]
        panes.append({"pane_id": pane_id, "pane_title": pane_title})
    return panes


def capture_pane(pane_id: str, tail_lines: int = 30) -> str:
    return run_tmux("capture-pane", "-p", "-t", pane_id, "-S", f"-{tail_lines}")


def load_latest_snapshots(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    latest: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                payload = json.loads(raw_line)
            except json.JSONDecodeError:
                continue

            name = str(payload.get("hcom_instance_name") or "").strip().lower()
            if not name:
                continue
            previous = latest.get(name)
            if previous is None or str(payload.get("ts") or "") >= str(previous.get("ts") or ""):
                latest[name] = payload
    return latest


def detect_agent_name(title: str) -> str | None:
    lowered = title.lower()
    for name in AGENT_ORDER:
        if name in lowered:
            return name
    return None


def parse_live_status(content: str) -> dict[str, Any]:
    context_used_pct: int | None = None
    current_usage: float | None = None
    model_display_name: str | None = None

    for line in reversed(content.splitlines()):
        if context_used_pct is None:
            match = STATUS_CONTEXT_RE.search(line)
            if match:
                context_used_pct = int(match.group(1))
        if current_usage is None:
            match = STATUS_COST_RE.search(line)
            if match:
                current_usage = float(match.group(1))
        if model_display_name is None:
            match = STATUS_MODEL_RE.search(line)
            if match:
                model_display_name = match.group(1)
        if context_used_pct is not None and (current_usage is not None or model_display_name is not None):
            break

    payload: dict[str, Any] = {}
    if context_used_pct is not None:
        payload["context_used_pct"] = context_used_pct
        payload["context_remaining_pct"] = max(0, 100 - context_used_pct)
    if current_usage is not None:
        payload["current_usage"] = current_usage
    if model_display_name is not None:
        payload["model_display_name"] = model_display_name
    return payload


def collect_live_status_snapshots(*, window_name: str, baseline: dict[str, dict[str, Any]], now_dt: datetime) -> dict[str, dict[str, Any]]:
    window_target = find_window_target(window_name)
    if not window_target:
        return {}

    live_snapshots: dict[str, dict[str, Any]] = {}
    for pane in list_window_panes(window_target):
        name = detect_agent_name(pane.get("pane_title", ""))
        if not name:
            continue
        live_status = parse_live_status(capture_pane(pane["pane_id"]))
        if not live_status:
            continue
        merged = dict(baseline.get(name, {}))
        merged.update(
            {
                "ts": now_dt.isoformat(),
                "tmux_pane": pane["pane_id"],
                "hcom_instance_name": name,
                "context_used_pct": live_status.get("context_used_pct"),
                "context_remaining_pct": live_status.get("context_remaining_pct"),
            }
        )
        if live_status.get("current_usage") is not None:
            merged["current_usage"] = live_status.get("current_usage")
        if live_status.get("model_display_name"):
            merged["model_display_name"] = live_status.get("model_display_name")
        live_snapshots[name] = merged
    return live_snapshots


def classify_agent_status(
    *,
    context_used_pct: int | None,
    age_seconds: float | None,
    heavy_threshold: int,
    critical_threshold: int,
    snapshot_stale_seconds: float,
) -> str:
    if age_seconds is None or age_seconds > snapshot_stale_seconds:
        return "stale"
    if context_used_pct is None:
        return "unknown"
    if context_used_pct >= critical_threshold:
        return "clear_or_reopen"
    if context_used_pct >= heavy_threshold:
        return "handoff_soon"
    return "heavy_ok"


def recommend_action(role: str, status: str) -> str:
    if role == "dispatcher":
        return "delegate_only"
    if role == "error_recorder":
        return "record_errors_only"
    if role == "context_monitor":
        return "monitor_and_route_only"
    if status == "missing":
        return "restart_or_reinject_context"
    if status == "stale":
        return "refresh_or_restart_agent"
    if status == "unknown":
        return "refresh_statusline_context"
    if status == "clear_or_reopen":
        return "handoff_then_clear_or_reopen"
    if status == "handoff_soon":
        return "handoff_before_heavy_work"
    return "heavy_ok"


def build_agent_record(name: str, snapshot: dict[str, Any] | None, *, now_dt: datetime, args: argparse.Namespace) -> dict[str, Any]:
    role = AGENT_ROLES.get(name, "worker")
    record: dict[str, Any] = {
        "name": name,
        "role": role,
        "session_id": None,
        "tmux_pane": None,
        "model": None,
        "context_used_pct": None,
        "context_remaining_pct": None,
        "current_usage": None,
        "snapshot_ts": None,
        "age_s": None,
        "status": "missing",
        "recommended_action": "restart_or_reinject_context",
        "heavy_work_allowed": False,
    }

    if snapshot is None:
        return record

    context_used = snapshot.get("context_used_pct")
    context_remaining = snapshot.get("context_remaining_pct")
    snapshot_ts = parse_iso(snapshot.get("ts"))
    age_s = round((now_dt - snapshot_ts).total_seconds(), 2) if snapshot_ts else None
    context_used_pct = int(context_used) if isinstance(context_used, (int, float)) else None
    context_remaining_pct = int(context_remaining) if isinstance(context_remaining, (int, float)) else None
    status = classify_agent_status(
        context_used_pct=context_used_pct,
        age_seconds=age_s,
        heavy_threshold=args.heavy_threshold,
        critical_threshold=args.critical_threshold,
        snapshot_stale_seconds=args.snapshot_stale_seconds,
    )

    heavy_work_allowed = role == "worker" and status == "heavy_ok"
    record.update(
        {
            "session_id": snapshot.get("session_id"),
            "tmux_pane": snapshot.get("tmux_pane"),
            "model": snapshot.get("model_display_name") or snapshot.get("model_id"),
            "context_used_pct": context_used_pct,
            "context_remaining_pct": context_remaining_pct,
            "current_usage": snapshot.get("current_usage"),
            "cost_total_usd": snapshot.get("cost_total_usd"),
            "snapshot_ts": snapshot.get("ts"),
            "age_s": age_s,
            "status": status,
            "recommended_action": recommend_action(role, status),
            "heavy_work_allowed": heavy_work_allowed,
        }
    )
    return record


def collect_agent_health(*, args: argparse.Namespace, now_dt: datetime) -> dict[str, Any]:
    latest_snapshots = load_latest_snapshots(Path(args.snapshots_file))
    live_snapshots = collect_live_status_snapshots(window_name=args.window_name, baseline=latest_snapshots, now_dt=now_dt)
    merged_snapshots = dict(latest_snapshots)
    merged_snapshots.update(live_snapshots)
    agents = [build_agent_record(name, merged_snapshots.get(name), now_dt=now_dt, args=args) for name in AGENT_ORDER]

    workers = [agent for agent in agents if agent["role"] == "worker"]
    heavy_ok_workers = [agent for agent in workers if agent["status"] == "heavy_ok"]
    handoff_workers = [agent for agent in workers if agent["status"] == "handoff_soon"]
    critical_workers = [agent for agent in workers if agent["status"] == "clear_or_reopen"]
    stale_agents = [agent["name"] for agent in agents if agent["status"] == "stale"]
    missing_agents = [agent["name"] for agent in agents if agent["status"] == "missing"]

    sorted_heavy_ok = sorted(
        heavy_ok_workers,
        key=lambda agent: (
            agent["context_used_pct"] if isinstance(agent["context_used_pct"], int) else 999,
            agent["age_s"] if isinstance(agent["age_s"], (int, float)) else 999999,
            agent["name"],
        ),
    )
    if missing_agents or stale_agents or critical_workers:
        overall_status = "degraded"
    elif handoff_workers:
        overall_status = "watch"
    else:
        overall_status = "healthy"

    return {
        "ts": now_dt.isoformat(),
        "thresholds": {
            "heavy_threshold_pct": args.heavy_threshold,
            "critical_threshold_pct": args.critical_threshold,
            "snapshot_stale_seconds": args.snapshot_stale_seconds,
        },
        "window_target": find_window_target(args.window_name),
        "agents": agents,
        "summary": {
            "overall_status": overall_status,
            "workers_total": len(workers),
            "worker_heavy_ok": len(heavy_ok_workers),
            "worker_handoff_soon": len(handoff_workers),
            "worker_clear_or_reopen": len(critical_workers),
            "stale_agents": stale_agents,
            "missing_agents": missing_agents,
            "freshest_workers": [agent["name"] for agent in sorted_heavy_ok[:2]],
            "best_heavy_candidates": [agent["name"] for agent in sorted_heavy_ok],
            "handoff_workers": [agent["name"] for agent in handoff_workers],
            "critical_workers": [agent["name"] for agent in critical_workers],
        },
    }


def summarize_block(block: dict[str, Any] | None, *, now_dt: datetime) -> dict[str, Any] | None:
    if not block:
        return None
    end_ts = parse_iso(block.get("actualEndTime")) or parse_iso(block.get("endTime"))
    age_minutes = round((now_dt - end_ts).total_seconds() / 60.0, 2) if end_ts else None
    return {
        "id": block.get("id"),
        "start_time": block.get("startTime"),
        "end_time": block.get("endTime"),
        "actual_end_time": block.get("actualEndTime"),
        "is_active": bool(block.get("isActive")),
        "is_gap": bool(block.get("isGap")),
        "entries": block.get("entries"),
        "total_tokens": block.get("totalTokens"),
        "cost_usd": block.get("costUSD"),
        "models": block.get("models") or [],
        "age_minutes": age_minutes,
    }


def collect_cc_usage(*, args: argparse.Namespace, now_dt: datetime) -> dict[str, Any]:
    completed = run_cmd(["bash", args.ccusage_script, "--json"], cwd=args.brain_root, timeout=args.command_timeout)
    result: dict[str, Any] = {"ok": completed.returncode == 0}
    if completed.returncode != 0:
        result["error"] = completed.stderr.strip() or completed.stdout.strip() or "ccusage_failed"
        return result
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "ccusage_invalid_json", "raw": completed.stdout[:500]}

    blocks = payload.get("blocks") or []
    active_block = next((block for block in reversed(blocks) if block.get("isActive") and not block.get("isGap")), None)
    latest_non_gap = next((block for block in reversed(blocks) if not block.get("isGap")), None)
    latest_gap = next((block for block in reversed(blocks) if block.get("isGap")), None)
    reference_block = active_block or latest_non_gap

    result["summary"] = {
        "blocks_total": len(blocks),
        "active_block_present": bool(active_block),
        "latest_block": summarize_block(reference_block, now_dt=now_dt),
        "latest_gap": summarize_block(latest_gap, now_dt=now_dt),
    }
    return result


def collect_codex_usage(*, args: argparse.Namespace) -> dict[str, Any]:
    completed = run_cmd(["bash", args.codexbar_script], cwd=args.brain_root, timeout=args.command_timeout)
    result: dict[str, Any] = {"ok": completed.returncode == 0}
    if completed.returncode != 0:
        result["error"] = completed.stderr.strip() or completed.stdout.strip() or "codexbar_failed"
        return result
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "codexbar_invalid_json", "raw": completed.stdout[:500]}

    entry = payload[0] if isinstance(payload, list) and payload else payload
    usage = entry.get("usage") or {}
    primary = usage.get("primary") or {}
    secondary = usage.get("secondary") or {}
    result["summary"] = {
        "provider": entry.get("provider"),
        "source": entry.get("source"),
        "version": entry.get("version"),
        "account_email": usage.get("accountEmail"),
        "primary": {
            "used_percent": primary.get("usedPercent"),
            "window_minutes": primary.get("windowMinutes"),
            "resets_at": primary.get("resetsAt"),
            "reset_description": primary.get("resetDescription"),
        },
        "secondary": {
            "used_percent": secondary.get("usedPercent"),
            "window_minutes": secondary.get("windowMinutes"),
            "resets_at": secondary.get("resetsAt"),
            "reset_description": secondary.get("resetDescription"),
        },
    }
    return result


def render_agent_health_lines(agents: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for agent in agents:
        context_used = agent.get("context_used_pct")
        context_text = f"{context_used}%" if isinstance(context_used, int) else "unknown"
        lines.append(
            f"- {agent['name']} ({agent['role']}): context={context_text}, status={agent['status']}, action={agent['recommended_action']}"
        )
    return "\n".join(lines)


def build_meaningful_task(workspace: str, health_payload: dict[str, Any], state_path: Path) -> str:
    summary = health_payload.get("summary", {})
    codex_usage = health_payload.get("codex_usage", {}).get("summary", {})
    cc_usage = health_payload.get("cc_usage", {}).get("summary", {})
    primary = codex_usage.get("primary", {})
    latest_block = cc_usage.get("latest_block", {})

    return f"""万物皆 6.0B。你当前通过网页 Codex 运行，处于被动唤醒模式。

PAL 6.0B 约束：
- fresh contexts 干重活
- 太一只负责分派，不亲自做实现
- 司过只负责记录错误
- 玄枢只负责监控 context / usage / idle
- 超过 40% context 的 worker 不适合重活，应先交接，再 clear 或 reopen

当前工作区：`{workspace}`

当前多 agent 健康摘要：
{render_agent_health_lines(health_payload.get("agents", []))}

关键摘要：
- overall_status: `{summary.get("overall_status")}`
- freshest_workers: `{", ".join(summary.get("freshest_workers", [])) or "none"}`
- handoff_workers: `{", ".join(summary.get("handoff_workers", [])) or "none"}`
- critical_workers: `{", ".join(summary.get("critical_workers", [])) or "none"}`
- codex 5h usage: `{primary.get("used_percent")}%`
- cc latest 5h block tokens: `{latest_block.get("total_tokens")}`

先检查这些文件，再决定一个最有意义的下一步并执行：
1. `{state_path}`
2. `~/.brain/shared_memory/recent/cc_agent_health.json`
3. `~/.brain/shared_memory/recent/cc_error_ledger.md`
4. `~/.brain/shared_memory/long_term/wushen_control.md`

执行要求：
1. 先用两三句话说明你选择的任务和理由。
2. 只做一个最高杠杆的下一步，不要空转，不要重复已完成工作。
3. 如果发现 worker 超过 40% 或监控有缺口，优先做 handoff / clear / reopen / detector 稳定性相关工作。
4. 完成后给出非常简短的结果和下一步建议。
"""


def maybe_nudge_codex(*, brain_root: str, label: str, workspace: str, health_payload: dict[str, Any], state_file: Path) -> dict[str, Any]:
    prompt = build_meaningful_task(workspace, health_payload, state_file)
    completed = run_cmd(
        ["bash", f"{brain_root}/scripts/codex.sh", "--web", "--label", label, prompt],
        cwd=brain_root,
        timeout=180.0,
    )
    payload: dict[str, Any] = {
        "ok": completed.returncode == 0,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }
    if completed.stdout.strip():
        try:
            payload["result"] = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload["result_raw"] = completed.stdout.strip()
    return payload


def cycle(
    args: argparse.Namespace,
    *,
    state_file: Path,
    log_file: Path,
    controller_state_file: Path,
    health_file: Path,
    health_log_file: Path,
) -> dict[str, Any]:
    detector_state = load_json(state_file)
    controller_state = load_json(controller_state_file)

    ensure_codex_tab(brain_root=args.brain_root, label=args.label)
    probe = probe_codex_state(brain_root=args.brain_root, label=args.label)

    now_dt = now()
    now_epoch = now_dt.timestamp()
    health_payload = collect_agent_health(args=args, now_dt=now_dt)
    health_payload["cc_usage"] = collect_cc_usage(args=args, now_dt=now_dt)
    health_payload["codex_usage"] = collect_codex_usage(args=args)
    write_json(health_file, health_payload)
    append_jsonl(health_log_file, health_payload)

    nudged = False
    nudge_result: dict[str, Any] | None = None

    if probe.get("ok") and probe.get("generating"):
        detector_state["last_generation_seen_at"] = now_dt.isoformat()
        detector_state["last_generation_seen_at_epoch"] = now_epoch

    last_activity_candidates = [
        controller_state.get("last_injected_at_epoch"),
        detector_state.get("last_generation_seen_at_epoch"),
        detector_state.get("last_nudge_at_epoch"),
    ]
    last_activity_epoch = max((float(value) for value in last_activity_candidates if isinstance(value, (int, float))), default=0.0)
    idle_for = now_epoch - last_activity_epoch if last_activity_epoch else now_epoch

    if probe.get("ok") and not probe.get("generating") and idle_for >= args.idle_threshold:
        nudge_result = maybe_nudge_codex(
            brain_root=args.brain_root,
            label=args.label,
            workspace=args.workspace,
            health_payload=health_payload,
            state_file=health_file,
        )
        nudged = bool(nudge_result.get("ok"))
        detector_state["last_nudge_at"] = now_dt.isoformat()
        detector_state["last_nudge_at_epoch"] = now_epoch

    detector_state["last_loop_at"] = now_dt.isoformat()
    detector_state["last_loop_at_epoch"] = now_epoch
    detector_state["last_probe"] = {
        "ok": probe.get("ok", False),
        "generating": probe.get("generating", False),
        "input_ready": probe.get("input_ready", False),
        "url": probe.get("url"),
        "title": probe.get("title"),
    }
    detector_state["last_health_summary"] = health_payload.get("summary", {})
    write_json(state_file, detector_state)

    codex_summary = health_payload.get("codex_usage", {}).get("summary", {})
    codex_primary = codex_summary.get("primary", {})
    event = {
        "ts": now_dt.isoformat(),
        "label": args.label,
        "probe_ok": probe.get("ok", False),
        "generating": probe.get("generating", False),
        "idle_for_s": round(idle_for, 2),
        "nudged": nudged,
        "health_overall_status": health_payload.get("summary", {}).get("overall_status"),
        "freshest_workers": health_payload.get("summary", {}).get("freshest_workers", []),
        "handoff_workers": health_payload.get("summary", {}).get("handoff_workers", []),
        "critical_workers": health_payload.get("summary", {}).get("critical_workers", []),
        "stale_agents": health_payload.get("summary", {}).get("stale_agents", []),
        "codex_primary_used_pct": codex_primary.get("used_percent"),
    }
    if nudge_result is not None:
        event["nudge_result"] = {"ok": nudge_result.get("ok", False), "stderr": nudge_result.get("stderr", "")}
    if not probe.get("ok"):
        event["probe_error"] = probe.get("error")
    append_jsonl(log_file, event)
    return event


def main() -> int:
    args = parse_args()
    state_file = Path(args.state_file)
    log_file = Path(args.log_file)
    controller_state_file = Path(args.controller_state)
    health_file = Path(args.health_file)
    health_log_file = Path(args.health_log_file)

    while True:
        result = cycle(
            args,
            state_file=state_file,
            log_file=log_file,
            controller_state_file=controller_state_file,
            health_file=health_file,
            health_log_file=health_log_file,
        )
        if args.once:
            print(json.dumps(result, ensure_ascii=False))
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
