#!/usr/bin/env python3
"""
Autonomous Agent Demo v2.0 - Self-Healing Edition
基于 Anthropic autonomous-coding 示例的主入口实现

NEW in v2.0:
- Self-healing trigger threshold (default: 3 consecutive failures)
- Deep failure trigger threshold (default: 10 consecutive failures)
- Structured history and decision tracking

Usage:
    # Basic usage
    python autonomous_agent_demo.py --project-dir ./my-project

    # With custom self-healing thresholds
    python autonomous_agent_demo.py --project-dir ./my-project \\
        --failed-trigger 5 \\
        --deep-failed-trigger 15

    # With custom model
    python autonomous_agent_demo.py --project-dir ./my-project \\
        --model claude-sonnet-4-5-20250929 \\
        --max-iterations 50
"""

import argparse
import asyncio
from pathlib import Path

from agent import run_autonomous_agent, FAILED_TRIGGER_THRESHOLD, DEEP_FAILED_THRESHOLD

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run autonomous coding agent v2.0 with Self-Healing mechanism"
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Path to the project directory (default: current directory)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Claude model to use (default: {DEFAULT_MODEL})"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=100,
        help="Maximum number of agent sessions (default: 100)"
    )

    parser.add_argument(
        "--initializer-prompt",
        type=Path,
        default=None,
        help="Path to initializer prompt file (default: project_dir/initializer_prompt.md)"
    )

    parser.add_argument(
        "--coding-prompt",
        type=Path,
        default=None,
        help="Path to coding prompt file (default: project_dir/coding_prompt.md)"
    )

    # === NEW: Self-healing parameters ===
    parser.add_argument(
        "--failed-trigger",
        type=int,
        default=FAILED_TRIGGER_THRESHOLD,
        help=f"Consecutive failures to trigger self-healing mode (default: {FAILED_TRIGGER_THRESHOLD})"
    )

    parser.add_argument(
        "--deep-failed-trigger",
        type=int,
        default=DEEP_FAILED_THRESHOLD,
        help=f"Consecutive failures to trigger deep failure/human intervention (default: {DEEP_FAILED_THRESHOLD})"
    )

    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()

    # Validate project directory
    if not args.project_dir.exists():
        print(f"Creating project directory: {args.project_dir}")
        args.project_dir.mkdir(parents=True)

    # Load custom prompts if provided
    initializer_prompt = None
    coding_prompt = None

    if args.initializer_prompt and args.initializer_prompt.exists():
        initializer_prompt = args.initializer_prompt.read_text()

    if args.coding_prompt and args.coding_prompt.exists():
        coding_prompt = args.coding_prompt.read_text()

    # Print configuration summary
    print()
    print("=" * 60)
    print("  Autonomous Agent v2.0 - Self-Healing Edition")
    print("=" * 60)
    print(f"  Project:       {args.project_dir}")
    print(f"  Model:         {args.model}")
    print(f"  Max Iterations: {args.max_iterations}")
    print(f"  Self-Healing:  {args.failed_trigger} consecutive failures")
    print(f"  Deep Failure:  {args.deep_failed_trigger} consecutive failures")
    print("=" * 60)
    print()

    # Run the autonomous agent
    await run_autonomous_agent(
        project_dir=args.project_dir,
        model=args.model,
        max_iterations=args.max_iterations,
        initializer_prompt=initializer_prompt,
        coding_prompt=coding_prompt,
        failed_trigger=args.failed_trigger,
        deep_failed_trigger=args.deep_failed_trigger
    )


if __name__ == "__main__":
    asyncio.run(main())
