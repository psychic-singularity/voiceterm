
from dataclasses import dataclass
import shlex


@dataclass
class PermissionResult:
    allowed: bool
    requires_confirmation: bool
    reason: str








# Exact commands permitted without confirmation.
SAFE_COMMANDS = {
    "pwd",
    "dir",
    "ls",
    "git status",
    "git diff",
    "git log",
    "docker ps",
    "pytest",
    "python --version",
    "py --version",
    "node --version",
    "npm test",
}

# These command names are never automatically permitted.
DANGEROUS_COMMANDS = {
    "del",
    "erase",
    "rmdir",
    "rd",
    "format",
    "shutdown",
    "taskkill",
    "rm",
    "kill",
}

MODIFYING_COMMANDS = {
    "git commit",
    "git checkout",
    "git switch",
    "git reset",
    "git push",
    "docker restart",
    "docker stop",
    "docker rm",
    "npm install",
    "pip install",
}

# Commands that can cause significant or destructive changes.
DANGEROUS_COMMANDS = {
    "del", "erase", "rmdir", "rd", "format",
    "shutdown", "taskkill", "rm", "kill",
}



def check_command(command: str) -> PermissionResult:
    """Classify a command before execution."""

    if not command or not command.strip():
        return PermissionResult(
            False, False, "Empty commands are not allowed."
        )

    try:
        parts = shlex.split(command, posix=False)
    except ValueError:
        return PermissionResult(
            False, False, "Could not parse the command."
        )

    if not parts:
        return PermissionResult(
            False, False, "Empty commands are not allowed."
        )

    # Reject command chaining and shell operators.
    # This intentionally errs on the side of caution.
    forbidden_chars = [";", "&&", "||", "|", ">", "<", "\n", "\r"]

    if any(char in command for char in forbidden_chars):
        return PermissionResult(
            False, False,
            "Shell operators and command chaining are not allowed."
        )

    executable = parts[0].lower().split("\\")[-1]
    normalized = " ".join(parts).lower()

    if executable in DANGEROUS_COMMANDS:
        return PermissionResult(
            False, True,
            "Potentially destructive command. Explicit approval required."
        )

    if any(
        normalized == item or normalized.startswith(item + " ")
        for item in MODIFYING_COMMANDS
    ):
        return PermissionResult(
            False, True,
            "This command can modify system or project state."
        )

    if normalized in SAFE_COMMANDS:
        return PermissionResult(
            True, False, "Approved read-only command."
        )

    return PermissionResult(
        False, False,
        "Command is not on the approved allowlist."
    )
