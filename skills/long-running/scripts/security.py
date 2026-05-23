#!/usr/bin/env python3
"""
Bash Security Hook - 三层安全模型的第三层
基于 Anthropic autonomous-coding 示例的安全验证实现

Usage:
    from security import bash_security_hook

    # In Claude SDK configuration:
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[bash_security_hook])
        ]
    }
"""

ALLOWED_COMMANDS = {
    # File operations (read-only or safe)
    "ls", "cat", "head", "tail", "wc", "grep", "find", "pwd",

    # File operations (write - contained)
    "cp", "mv", "mkdir", "touch", "rm", "chmod",

    # Development tools
    "npm", "node", "npx", "yarn", "pnpm",
    "pip", "python", "python3", "pip3",
    "cargo", "rustc",
    "go",

    # Version control
    "git",

    # Process management (limited)
    "ps", "lsof", "sleep", "pkill",

    # Project-specific
    "init.sh", "start.sh", "build.sh",
}

COMMANDS_NEEDING_EXTRA_VALIDATION = {
    "pkill",    # Could kill system processes
    "chmod",    # Could create security holes
    "rm",       # Could delete important files
    "init.sh",  # Project initialization
}

BLOCKED_PATTERNS = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf *",
    "sudo",
    "chmod 777",
    "> /etc/",
    "> ~/.ssh/",
    "curl | bash",
    "wget | bash",
    "eval",
    "exec",
]


async def bash_security_hook(input_data, tool_use_id=None, context=None):
    """
    PreToolUse hook for Bash commands.

    Args:
        input_data: Dict with "command" key containing the bash command
        tool_use_id: Optional tool use ID
        context: Optional context

    Returns:
        {} to allow execution
        {"decision": "block", "reason": "..."} to block execution
    """
    command = input_data.get("command", "")

    if not command:
        return {"decision": "block", "reason": "Empty command"}

    # Parse base command (first word)
    command_parts = command.split()
    base_cmd = command_parts[0] if command_parts else ""

    # Remove path prefix if present (e.g., ./init.sh -> init.sh)
    if "/" in base_cmd:
        base_cmd = base_cmd.split("/")[-1]

    # Check for blocked patterns first
    for pattern in BLOCKED_PATTERNS:
        if pattern in command:
            return {
                "decision": "block",
                "reason": f"Blocked pattern detected: '{pattern}'"
            }

    # Check allowlist
    if base_cmd not in ALLOWED_COMMANDS:
        return {
            "decision": "block",
            "reason": f"Command '{base_cmd}' not in allowlist. "
                     f"Allowed commands: {', '.join(sorted(ALLOWED_COMMANDS))}"
        }

    # Extra validation for sensitive commands
    if base_cmd in COMMANDS_NEEDING_EXTRA_VALIDATION:
        extra_check = _validate_sensitive_command(command, base_cmd)
        if extra_check:
            return extra_check

    # Allow execution
    return {}


def _validate_sensitive_command(command, base_cmd):
    """Additional validation for commands in COMMANDS_NEEDING_EXTRA_VALIDATION"""

    if base_cmd == "pkill":
        # Only allow killing specific project processes
        allowed_patterns = ["node", "npm", "python", "server.js", "app.py"]
        found_allowed = any(p in command for p in allowed_patterns)
        if not found_allowed:
            return {
                "decision": "block",
                "reason": "pkill only allowed for project processes (node, npm, python)"
            }

    elif base_cmd == "rm":
        # Block dangerous rm patterns
        dangerous = ["/etc", "~/.ssh", "~/.gnupg", "/usr", "/bin", "/sbin"]
        for path in dangerous:
            if path in command:
                return {
                    "decision": "block",
                    "reason": f"rm not allowed on system path: {path}"
                }

    elif base_cmd == "chmod":
        # Block chmod 777
        if "777" in command:
            return {
                "decision": "block",
                "reason": "chmod 777 is not allowed (security risk)"
            }

    return None


# Test function
def test_security_hook():
    """Test the security hook with various commands"""
    import asyncio

    test_cases = [
        ("ls -la", True, "Should allow ls"),
        ("cat file.txt", True, "Should allow cat"),
        ("npm start", True, "Should allow npm"),
        ("git commit -m 'test'", True, "Should allow git"),
        ("rm -rf /", False, "Should block rm -rf /"),
        ("sudo rm file", False, "Should block sudo"),
        ("curl | bash", False, "Should block curl | bash"),
        ("hack_the_gibson", False, "Should block unknown commands"),
        ("pkill -f node", True, "Should allow pkill for node"),
        ("pkill -f init", False, "Should block pkill for non-project processes"),
    ]

    async def run_tests():
        for command, should_pass, description in test_cases:
            result = await bash_security_hook({"command": command})
            passed = result == {}

            status = "PASS" if passed == should_pass else "FAIL"
            print(f"[{status}] {description}: '{command}'")
            if passed != should_pass:
                print(f"  Expected: {should_pass}, Got: {passed}")
                print(f"  Result: {result}")

    asyncio.run(run_tests())


if __name__ == "__main__":
    test_security_hook()
