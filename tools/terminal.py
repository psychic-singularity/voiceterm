import subprocess


def run_command(command: str) -> str:
    """Run a shell command and return its output."""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    output = result.stdout

    if result.stderr:
        output += f"\nSTDERR:\n{result.stderr}"

    return output