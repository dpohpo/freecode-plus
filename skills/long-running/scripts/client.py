#!/usr/bin/env python3
"""
Claude Agent SDK Client Factory
基于 Anthropic autonomous-coding 示例的 SDK 配置实现

Requirements:
    pip install claude-code-sdk

Usage:
    from client import create_client

    client = create_client(
        project_dir=Path("/path/to/project"),
        model="claude-sonnet-4-5-20250929"
    )

    async for message in client.run(messages=[...]):
        print(message)
"""

from pathlib import Path
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions, HookMatcher

# Puppeteer MCP tools for browser automation
PUPPETEER_TOOLS = [
    "mcp__puppeteer__puppeteer_navigate",
    "mcp__puppeteer__puppeteer_screenshot",
    "mcp__puppeteer__puppeteer_click",
    "mcp__puppeteer__puppeteer_type",
    "mcp__puppeteer__puppeteer_evaluate",
]

# Built-in tools for code manipulation
BUILTIN_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
]

# Import security hook
try:
    from security import bash_security_hook
except ImportError:
    async def bash_security_hook(input_data, tool_use_id=None, context=None):
        """Fallback: allow all commands if security.py not available"""
        print("WARNING: Security hook not available, allowing all commands")
        return {}


def create_client(project_dir: Path, model: str = "claude-sonnet-4-5-20250929") -> ClaudeSDKClient:
    """
    Create a Claude SDK client with security-hardened configuration.

    Args:
        project_dir: Path to the project directory
        model: Claude model to use

    Returns:
        Configured ClaudeSDKClient instance
    """
    # Security configuration
    security_settings = {
        "sandbox": {
            "enabled": True,
            "autoAllowBashIfSandboxed": True,
        },
        "permissions": {
            "defaultMode": "acceptEdits",
            "allow": [
                {"tool": "Read"},
                {"tool": "Write"},
                {"tool": "Edit"},
                {"tool": "Glob"},
                {"tool": "Grep"},
                {"tool": "Bash"},
            ],
        },
    }

    # MCP server configuration for browser automation
    mcp_servers = {
        "puppeteer": {
            "command": "npx",
            "args": ["puppeteer-mcp-server"],
        }
    }

    # Hook configuration for Bash security
    hooks = {
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[bash_security_hook])
        ]
    }

    # Create client with all configuration
    client = ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=model,
            allowed_tools=[*BUILTIN_TOOLS, *PUPPETEER_TOOLS],
            mcp_servers=mcp_servers,
            hooks=hooks,
            max_turns=1000,
            cwd=str(project_dir.resolve()),
            security=security_settings,
        )
    )

    return client


def create_minimal_client(project_dir: Path, model: str = "claude-sonnet-4-5-20250929") -> ClaudeSDKClient:
    """
    Create a minimal client without browser automation (for simpler projects).

    Args:
        project_dir: Path to the project directory
        model: Claude model to use

    Returns:
        Configured ClaudeSDKClient instance with minimal tools
    """
    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=model,
            allowed_tools=BUILTIN_TOOLS,
            max_turns=1000,
            cwd=str(project_dir.resolve()),
        )
    )


# Test function
async def test_client_creation():
    """Test that client can be created"""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Test full client
        client = create_client(project_dir)
        print(f"Full client created: {client}")

        # Test minimal client
        minimal = create_minimal_client(project_dir)
        print(f"Minimal client created: {minimal}")

        print("Client creation test passed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_client_creation())
