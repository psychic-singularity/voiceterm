
import pytest

from security import pending_actions
from tools.filesystem import (
    resolve_path,
    list_directory,
    read_file,
    search_files,
    create_file,
)


def test_list_directory():
    output = list_directory(".")
    assert "main.py" in output or "FILE main.py" in output


def test_read_existing_file():
    output = read_file("main.py")
    assert isinstance(output, str)
    assert output


def test_read_missing_file():
    output = read_file("file_that_does_not_exist.txt")
    assert "Error" in output


def test_reject_path_outside_project():
    with pytest.raises(ValueError):
        resolve_path("../../../../Windows/win.ini")


def test_search_existing_text():
    output = search_files("create_react_agent", ".")
    assert "create_react_agent" in output


def test_create_file_requires_confirmation_and_creates_after_confirm(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pending_actions.pending_action = None

    result = create_file("notes.txt", "hello world")
    assert "CONFIRMATION_REQUIRED: Create file 'notes.txt'?" in result
    assert pending_actions.pending_action["type"] == "create_file"
    assert not (tmp_path / "notes.txt").exists()

    outcome = pending_actions.confirm_pending_action()

    assert "Created:" in outcome
    assert (tmp_path / "notes.txt").read_text(encoding="utf-8") == "hello world"
