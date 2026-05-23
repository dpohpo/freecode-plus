#!/usr/bin/env python3
"""Resolve the source model/provider context for yqhsq launches.

The caller may be started with a provider model via CLI flags instead of
ANTHROPIC_MODEL in the shell env, e.g.:

  free-code --bare --settings ~/.config/free-code/freeds.settings.json --model deepseek-v4-pro

This helper walks the parent process chain, reads the nearest --model and
--settings values, merges settings.env with the current process env, and emits a
shell fragment that launch.sh can source.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


BASE_ENV_KEYS = [
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_SMALL_FAST_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME",
    "ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_DESCRIPTION",
    "ANTHROPIC_CUSTOM_MODEL_OPTION",
    "ANTHROPIC_CUSTOM_MODEL_OPTION_NAME",
    "ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION",
    "CLAUDE_CODE_SUBAGENT_MODEL",
    "CLAUDE_CODE_EFFORT_LEVEL",
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS",
    "CLAUDE_CODE_TEAMMATE_COMMAND",
    "API_TIMEOUT_MS",
    "FREEGLM_TEAM_LAYOUT",
    "FREECODE_AGENT_TEAM_LAYOUT",
    "BUN_BIN",
    "FREECODE_AGENT_TEAM_MODEL_PROFILES",
    "FREECODE_AGENT_TEAM_GENERATED_SETTINGS_DIR",
]


def shell_assign(name: str, value: str) -> str:
    return f"{name}={shlex.quote(value)}"


def shell_array(name: str, values: list[str]) -> str:
    return f"{name}=(" + " ".join(shlex.quote(value) for value in values) + ")"


def ps_field(pid: int, field: str) -> str:
    result = subprocess.run(
        ["ps", "-o", f"{field}=", "-p", str(pid)],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def ancestor_args(start_pid: int) -> list[list[str]]:
    args_list: list[list[str]] = []
    seen: set[int] = set()
    pid = start_pid
    while pid > 1 and pid not in seen:
        seen.add(pid)
        raw = ps_field(pid, "args")
        if raw:
            try:
                args_list.append(shlex.split(raw))
            except ValueError:
                args_list.append(raw.split())
        parent = ps_field(pid, "ppid")
        try:
            pid = int(parent)
        except ValueError:
            break
    return args_list


def find_flag(args_list: list[list[str]], flag: str) -> str | None:
    for args in args_list:
        for index, arg in enumerate(args):
            if arg == flag and index + 1 < len(args):
                return args[index + 1]
            if arg.startswith(f"{flag}="):
                return arg.split("=", 1)[1]
    return None


def find_flags(args_list: list[list[str]], flag: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for args in args_list:
        for index, arg in enumerate(args):
            value: str | None = None
            if arg == flag and index + 1 < len(args):
                value = args[index + 1]
            elif arg.startswith(f"{flag}="):
                value = arg.split("=", 1)[1]
            if value and value not in seen:
                seen.add(value)
                values.append(value)
    return values


def has_flag(args_list: list[list[str]], flag: str) -> bool:
    return any(flag in args for args in args_list)


def truthy(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "y", "on"}


def detect_source_tool(args_list: list[list[str]], settings_path: str) -> str:
    haystacks = [" ".join(args).lower() for args in args_list]
    if settings_path:
        haystacks.append(settings_path.lower())
    joined = "\n".join(haystacks)
    if (
        "free-code" in joined
        or "cli-dev" in joined
        or "--teammate-mode" in joined
        or ".config/free-code" in joined
    ):
        return "freecode"
    if "claude" in joined or "@anthropic-ai/claude-code" in joined:
        return "claude"
    return ""


def expand_path(raw: str | None) -> str:
    if not raw:
        return ""
    return str(Path(os.path.expandvars(os.path.expanduser(raw))).resolve())


def read_settings(path: str) -> dict[str, Any]:
    if not path:
        return {}
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}


def normalize_model(model: str) -> str:
    return model.strip()


def safe_env(settings_env: Any) -> dict[str, str]:
    if not isinstance(settings_env, dict):
        return {}
    out: dict[str, str] = {}
    for key, value in settings_env.items():
        if not isinstance(key, str):
            continue
        if not key.replace("_", "A").isalnum() or key[0].isdigit():
            continue
        if value is None:
            continue
        out[key] = str(value)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--initial-model", default="")
    parser.add_argument("--initial-settings", default="")
    parser.add_argument("--initial-bare", default="")
    parser.add_argument("--initial-tool", default="")
    parser.add_argument("--initial-add-dir", action="append", default=[])
    parser.add_argument("--start-pid", type=int, default=os.getpid())
    args = parser.parse_args()

    parents = ancestor_args(args.start_pid)
    arg_model = find_flag(parents, "--model") or ""
    arg_settings = find_flag(parents, "--settings") or ""
    source_add_dirs = [
        expand_path(value)
        for value in [*args.initial_add_dir, *find_flags(parents, "--add-dir")]
    ]

    settings_path = expand_path(args.initial_settings or arg_settings)
    source_tool = args.initial_tool or detect_source_tool(parents, settings_path)
    source_bare = truthy(args.initial_bare) or has_flag(parents, "--bare")
    settings = read_settings(settings_path)
    settings_env = safe_env(settings.get("env"))

    model = normalize_model(
        args.initial_model
        or os.environ.get("YQHSQ_MODEL", "")
        or os.environ.get("ANTHROPIC_MODEL", "")
        or arg_model
        or str(settings.get("model") or "")
        or settings_env.get("ANTHROPIC_MODEL", "")
        or settings_env.get("ANTHROPIC_CUSTOM_MODEL_OPTION", "")
        or os.environ.get("ANTHROPIC_CUSTOM_MODEL_OPTION", "")
    )

    merged_env: dict[str, str] = {}
    for key in BASE_ENV_KEYS:
        value = os.environ.get(key)
        if value:
            merged_env[key] = value
    merged_env.update(settings_env)
    if model:
        merged_env["ANTHROPIC_MODEL"] = model
    if "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" not in merged_env:
        merged_env["CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"] = "1"
    if "FREEGLM_TEAM_LAYOUT" not in merged_env:
        merged_env["FREEGLM_TEAM_LAYOUT"] = "grid"
    if "FREECODE_AGENT_TEAM_LAYOUT" not in merged_env:
        merged_env["FREECODE_AGENT_TEAM_LAYOUT"] = "grid"

    context_keys = sorted(set(BASE_ENV_KEYS) | set(merged_env))
    print(shell_assign("YQHSQ_MODEL", model))
    print(shell_assign("YQHSQ_SOURCE_SETTINGS", settings_path))
    print(shell_assign("YQHSQ_SOURCE_BARE", "1" if source_bare else "0"))
    print(shell_assign("YQHSQ_SOURCE_MODEL_ARG", arg_model))
    print(shell_assign("YQHSQ_SOURCE_TOOL", source_tool))
    print(shell_array("YQHSQ_SOURCE_ADD_DIRS", source_add_dirs))
    print(shell_array("YQHSQ_CONTEXT_ENV_KEYS", context_keys))
    for key in context_keys:
        value = merged_env.get(key)
        if value:
            print(f"export {shell_assign(key, value)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
