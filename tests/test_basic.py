import tempfile
from pathlib import Path
import pytest

from dirscribe.core import (
    export_directory_structure,
    scan_directory
)


def test_scan_empty_directory():
    """
    Tests scanning an empty directory. The result should have no children.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        tree = scan_directory(tmp_path)
        assert tree["type"] == "directory"
        assert len(tree["children"]) == 0


def test_skip_hidden():
    """
    Tests that hidden files and directories are skipped when skip_hidden=True.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create a hidden file
        hidden_file = tmp_path / ".hidden.txt"
        hidden_file.write_text("This is hidden", encoding="utf-8")

        # Create a normal file
        visible_file = tmp_path / "visible.txt"
        visible_file.write_text("This is visible", encoding="utf-8")

        tree = scan_directory(tmp_path, skip_hidden=True)
        # Should see only the visible file
        children_names = [child["name"] for child in tree["children"]]
        assert "visible.txt" in children_names
        assert ".hidden.txt" not in children_names


def test_max_size():
    """
    Tests that files exceeding max_size do not have their content read.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        big_file = tmp_path / "bigfile.txt"
        # Write a large content
        big_file.write_text("A" * 5000, encoding="utf-8")

        small_file = tmp_path / "smallfile.txt"
        small_file.write_text("Short content", encoding="utf-8")

        tree = scan_directory(tmp_path, include_extensions=[".txt"], max_size=1000)
        big_entry = next(child for child in tree["children"] if child["name"] == "bigfile.txt")
        small_entry = next(child for child in tree["children"] if child["name"] == "smallfile.txt")

        # big file content should be replaced by a skip message
        assert "content" in big_entry
        assert "exceeds 1000 bytes" in big_entry["content"]
        # small file should contain actual content
        assert small_entry["content"] == "Short content"


def test_show_metadata():
    """
    Tests that file metadata is included when show_metadata=True.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        f = tmp_path / "example.txt"
        f.write_text("Hello World", encoding="utf-8")

        tree = scan_directory(tmp_path, include_extensions=[".txt"], show_metadata=True)
        file_node = tree["children"][0]
        assert "metadata" in file_node
        assert "size" in file_node["metadata"]
        assert file_node["metadata"]["size"] == len("Hello World")


def test_json_output():
    """
    Tests the export_directory_structure output in JSON format.
    Ensures the returned string can be parsed as JSON.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        (tmp_path / "test.py").write_text("print('test')", encoding="utf-8")

        output = export_directory_structure(
            target_dir=tmp_path,
            include_extensions=[".py"],
            output_format="json"
        )
        import json
        parsed = json.loads(output)
        assert parsed["type"] == "directory"
        assert parsed["children"][0]["name"] == "test.py"
        assert "print('test')" in parsed["children"][0].get("content", "")


if __name__ == "__main__":
    pytest.main([__file__])
