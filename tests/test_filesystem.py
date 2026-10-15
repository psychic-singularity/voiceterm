
import pytest
    

from tools.filesystem import (
    resolve_path,
    list_directory,
    read_file,
    search_files,
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
