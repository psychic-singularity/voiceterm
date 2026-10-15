
from pathlib import Path

PROJECT_ROOT = Path.cwd().resolve()

pending_action = None


def resolve_project_path(path: str) -> Path:
    """Resolve a path and reject targets outside the project root."""
    target = (PROJECT_ROOT / path).resolve()

    if not target.is_relative_to(PROJECT_ROOT):
        raise ValueError("Path is outside the project directory.")

    return target


def request_delete(path: str) -> str:
    """Register a file deletion for confirmation."""
    global pending_action

    try:
        target = resolve_project_path(path)

        if not target.is_file():
            return f"Error: File does not exist: {path}"

        pending_action = {
            "type": "delete_file",
            "path": target,
        }

        return (
            f"CONFIRMATION_REQUIRED: Delete file "
            f"'{target.relative_to(PROJECT_ROOT)}'? "
            "Type y to confirm or n to cancel."
        )

    except (OSError, ValueError) as exc:
        return f"Error requesting file deletion: {exc}"


def request_create_file(path: str) -> str:
    """Register creation of an empty file for confirmation."""
    global pending_action

    try:
        target = resolve_project_path(path)

        if target.exists():
            return f"Error: Target already exists: {path}"

        if not target.parent.is_dir():
            return f"Error: Parent directory does not exist: {target.parent}"

        pending_action = {
            "type": "create_file",
            "path": target,
        }

        return (
            f"CONFIRMATION_REQUIRED: Create file "
            f"'{target.relative_to(PROJECT_ROOT)}'? "
            "Type y to confirm or n to cancel."
        )

    except (OSError, ValueError) as exc:
        return f"Error requesting file creation: {exc}"


def confirm_pending_action() -> str:
    """Execute the exact pending action after user confirmation."""
    global pending_action

    action = pending_action

    if action is None:
        return "No pending action."

    # Consume the pending action so it cannot be reused.
    pending_action = None

    try:
        target = action["path"]
        operation = action["type"]

        # Revalidate the path immediately before execution.
        resolved = target.resolve()

        if not resolved.is_relative_to(PROJECT_ROOT):
            return "Error: Target is outside the project."

        if operation == "delete_file":
            if not resolved.is_file():
                return "Error: Target no longer exists or is not a file."

            resolved.unlink()
            return f"Deleted: {resolved.relative_to(PROJECT_ROOT)}"

        elif operation == "create_file":
            if resolved.exists():
                return "Error: Target already exists. Nothing was created."

            if not resolved.parent.is_dir():
                return "Error: Parent directory no longer exists."

            # Exclusive creation prevents overwriting an existing file.
            with resolved.open("x", encoding="utf-8"):
                pass

            return f"Created: {resolved.relative_to(PROJECT_ROOT)}"

        return f"Error: Unsupported action type: {operation}"

    except OSError as exc:
        return f"Error executing pending action: {exc}"


def cancel_pending_action() -> str:
    """Cancel the pending action without executing it."""
    global pending_action

    if pending_action is None:
        return "No pending action."

    operation = pending_action["type"]
    pending_action = None

    if operation == "create_file":
        return "File creation cancelled. Nothing was created."

    return "File deletion cancelled. Nothing was deleted."
