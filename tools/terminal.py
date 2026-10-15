
import shlex
import subprocess

from rich.console import Console
from rich.panel import Panel

from security.permissions import check_command

console = Console()
MAX_OUTPUT = 12_000


def run_command(command: str) -> str:
    """Execute an approved command or request user confirmation."""

    permission = check_command(command)

    if not permission.allowed:
        console.print(
            Panel(
                f"[bold yellow]Command requires approval[/bold yellow]\n\n"
                f"[bold]Command:[/bold] {command}\n"
                f"[dim]{permission.reason}[/dim]",
                title="VoiceTerm Security",
                border_style="yellow",
            )
        )

        answer = console.input(
            "[bold yellow]Execute this command? [y/N] > [/bold yellow]"
        ).strip().lower()

        if answer != "y":
            return "Command cancelled by user. Nothing was executed."

    # Never pass the model's raw command to a shell.
    try:
        parts = shlex.split(command, posix=False)
        parts = [
            part[1:-1]
            if len(part) >= 2 and part[0] == part[-1]
            and part[0] in ("'", '"')
            else part
            for part in parts
        ]

        if not parts:
            return "Error: Empty command."

        result = subprocess.run(
            parts,
            shell=False,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=None,
        )

        output = result.stdout or ""

        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"

        if result.returncode != 0:
            output = (
                f"Exit code: {result.returncode}\n"
                + output
            )

        if not output.strip():
            output = "Command completed with no output."

        if len(output) > MAX_OUTPUT:
            output = output[:MAX_OUTPUT] + "\n... output truncated"

        return output

    except FileNotFoundError:
        return "Error: Executable not found. Check the command and PATH."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except (OSError, ValueError) as exc:
        return f"Error executing command: {exc}"
