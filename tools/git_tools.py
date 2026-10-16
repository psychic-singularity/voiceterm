
import subprocess
from pathlib import Path


def get_project_root() -> Path:
    """Return the active project root for the current working directory."""
    return Path.cwd().resolve()


def run_git(*args: str) -> str:
    """Run a read-only Git command in the VoiceTerm project."""
    project_root = get_project_root()
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=15,
            shell=False,
        )

        output = result.stdout.strip()

        if result.returncode != 0:
            error = result.stderr.strip()
            return f"Git error (exit code {result.returncode}): {error}"

        return output or "No output."

    except FileNotFoundError:
        return "Error: Git is not installed or not on PATH."
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out."


def git_status() -> str:
    """Show the working tree status."""
    return run_git("status", "--short", "--branch")


def git_diff() -> str:
    """Show changes to tracked, unstaged files."""
    output = run_git("diff", "--no-ext-diff", "--", ".")

    if len(output) > 20_000:
        output = output[:20_000] + "\n... diff truncated"

    return output


def git_log() -> str:
    """Show the most recent five commits."""
    return run_git(
        "log", "-5", "--oneline", "--decorate"
    )
