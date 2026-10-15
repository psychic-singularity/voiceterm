from pathlib import Path
from security.pending_actions import request_delete,request_create_file

# Use the directory from which VoiceTerm is launched.
PROJECT_ROOT = Path.cwd().resolve()
IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
}

def resolve_path(path: str) -> Path:
    """Resolve a path and prevent access outside the project root."""
    target = (PROJECT_ROOT / path).resolve()

    if not target.is_relative_to(PROJECT_ROOT):
        raise ValueError("Access outside the project directory is not allowed.")

    return target


def list_directory(path: str = ".") -> str:
    """List files and directories at a project-relative path."""
    try:
        directory = resolve_path(path)
    
        if not directory.is_dir():
            return f"Error: Not a directory: {path}"

        entries = sorted(
            directory.iterdir(),
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )

        results = []

        for entry in entries[:200]:
            if entry.is_dir() and entry.name in IGNORED_DIRS:
                continue

            kind = "DIR " if entry.is_dir() else "FILE"
            results.append(f"{kind} {entry.name}")

        if not results:
            return "Directory is empty."

        output = "\n".join(results)

        if len(entries) > 200:
            output += "\n... output truncated"

        return output

    except (OSError, ValueError) as exc:
        return f"Error listing directory: {exc}"


def read_file(path: str) -> str:
    """Read a UTF-8 text file inside the project."""
    try:
        file_path = resolve_path(path)

        if not file_path.is_file():
            return f"Error: File not found: {path}"

        if file_path.stat().st_size > 1_000_000:
            return "Error: File exceeds the 1 MB reading limit."

        return file_path.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        return "Error: File is not valid UTF-8 text."
    except (OSError, ValueError) as exc:
        return f"Error reading file: {exc}"


def search_files(query: str, path: str = ".") -> str:
    """Search text files for a case-insensitive string."""
    if not query.strip():
        return "Error: Search query cannot be empty."

    try:
        root = resolve_path(path)

        if not root.is_dir():
            return f"Error: Not a directory: {path}"

        results = []
        max_results = 50
        max_file_size = 1_000_000

        for file_path in root.rglob("*"):
            if any(part in IGNORED_DIRS for part in file_path.parts):
                continue

            if not file_path.is_file():
                continue

            try:
                if file_path.stat().st_size > max_file_size:
                    continue

                content = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            for line_number, line in enumerate(content.splitlines(), 1):
                if query.casefold() in line.casefold():
                    relative = file_path.relative_to(PROJECT_ROOT)
                    results.append(
                        f"{relative}:{line_number}: {line.strip()[:200]}"
                    )

                    if len(results) >= max_results:
                        return "\n".join(results) + "\n... results truncated"

        return "\n".join(results) if results else "No matches found."

    except (OSError, ValueError) as exc:
        return f"Error searching files: {exc}"

def delete_file(path: str) -> str:
    """Request confirmation before deleting a project file."""
    return request_delete(path)

def create_file(path: str)->str:
    """Request confirmation before deleting a project file."""
    return request_create_file(path)

    