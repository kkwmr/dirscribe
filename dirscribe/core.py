#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import time
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Tuple


#: A default dictionary for mapping file extensions to language names.
LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".rb": "Ruby",
    ".php": "PHP",
    ".html": "HTML",
    ".css": "CSS",
    ".cpp": "C++",
    ".c": "C",
    ".go": "Go",
    ".rs": "Rust",
    ".swift": "Swift",
}


def scan_directory(
    target_dir: Path,
    include_extensions: Optional[List[str]] = None,
    skip_hidden: bool = False,
    max_size: Optional[int] = None,
    show_metadata: bool = False,
    detect_language: bool = False
) -> Dict[str, Any]:
    """
    Recursively scans the target directory and builds a nested dictionary
    representing directories and files. File contents are included only for
    certain extensions if specified. Additional features include skipping hidden
    files/folders, limiting file read size, adding metadata, and detecting
    programming language based on file extension.

    Args:
        target_dir (Path):
            The directory path to scan.
        include_extensions (List[str], optional):
            List of file extensions (e.g., [".py", ".txt"]) whose contents
            should be included. If None or empty, contents are not included.
        skip_hidden (bool):
            If True, hidden files and directories (name starts with '.') are skipped.
        max_size (int, optional):
            Maximum file size (in bytes) to read. Files exceeding this size
            will not have their contents read.
        show_metadata (bool):
            If True, include file metadata (size, modification time).
        detect_language (bool):
            If True, attach a "language" field in the result based on file extension.

    Returns:
        Dict[str, Any]:
            A nested dictionary structure describing the directory tree.
            Example structure:
            {
              "type": "directory",
              "name": "some_dir",
              "path": "/absolute/path/to/some_dir",
              "children": [
                {
                  "type": "file",
                  "name": "main.py",
                  "path": "...",
                  "language": "Python",
                  "content": "...",
                  "metadata": {...}
                },
                ...
              ]
            }
    """
    if not target_dir.exists():
        return {
            "type": "error",
            "message": f"Directory does not exist: {target_dir}"
        }

    tree = {
        "type": "directory",
        "name": target_dir.name,
        "path": str(target_dir.resolve()),
        "children": []
    }

    try:
        entries = sorted(target_dir.iterdir(), key=lambda x: x.name.lower())
    except PermissionError:
        tree["children"].append({
            "type": "error",
            "message": f"Permission denied: {target_dir}"
        })
        return tree

    for entry in entries:
        # Skip hidden files/directories if skip_hidden == True
        if skip_hidden and entry.name.startswith('.'):
            continue

        if entry.is_dir():
            subtree = scan_directory(
                entry,
                include_extensions=include_extensions,
                skip_hidden=skip_hidden,
                max_size=max_size,
                show_metadata=show_metadata,
                detect_language=detect_language
            )
            tree["children"].append(subtree)
        else:
            file_node = {
                "type": "file",
                "name": entry.name,
                "path": str(entry.resolve())
            }

            # Detect language if requested
            if detect_language:
                lang = LANGUAGE_MAP.get(entry.suffix.lower())
                if lang:
                    file_node["language"] = lang

            # Show metadata if requested
            if show_metadata:
                file_node["metadata"] = _get_file_metadata(entry)

            # Include file content if extension is in include_extensions
            if include_extensions and len(include_extensions) > 0:
                if entry.suffix.lower() in [ext.lower() for ext in include_extensions]:
                    if max_size is not None and entry.stat().st_size > max_size:
                        file_node["content"] = f"<<File size exceeds {max_size} bytes, skipping content>>"
                    else:
                        file_node["content"] = _read_file_content(entry)
            tree["children"].append(file_node)

    return tree


def build_text_output(tree: Dict[str, Any], indent_level: int = 0) -> List[str]:
    """
    Builds a list of text lines (ASCII tree style) from the nested dictionary.

    Args:
        tree (Dict[str, Any]):
            A dictionary structure as returned by scan_directory().
        indent_level (int):
            Internal parameter for recursion to manage text indentation.

    Returns:
        List[str]:
            A list of lines representing the directory tree and file contents.
    """
    lines = []

    node_type = tree.get("type")
    node_name = tree.get("name", "unknown")

    if node_type == "error":
        msg = tree.get("message", "Unknown error")
        lines.append("  " * indent_level + f"[Error] {msg}")
        return lines

    if node_type == "directory":
        lines.append("  " * indent_level + f"📁 {node_name}/")
        children = tree.get("children", [])
        for child in children:
            lines.extend(build_text_output(child, indent_level + 1))

    elif node_type == "file":
        # Show file with language if present
        language = tree.get("language")
        if language:
            lines.append("  " * indent_level + f"📄 {node_name} ({language})")
        else:
            lines.append("  " * indent_level + f"📄 {node_name}")

        content = tree.get("content")
        if content is not None:
            for c_line in content.splitlines():
                lines.append("  " * (indent_level + 1) + c_line)

        metadata = tree.get("metadata")
        if metadata:
            lines.append("  " * (indent_level + 1) + f"[Metadata] Size: {metadata['size']} bytes")
            lines.append("  " * (indent_level + 1) + f"[Metadata] Modified: {metadata['modified']}")

    return lines


def export_directory_structure(
    target_dir: Path,
    include_extensions: Optional[List[str]] = None,
    skip_hidden: bool = False,
    max_size: Optional[int] = None,
    show_metadata: bool = False,
    detect_language: bool = False,
    output_format: str = "text",
    output_file: Optional[Path] = None
) -> Union[List[str], str]:
    """
    Scans the directory and produces output in either text or JSON format.
    Optionally writes the result to a file if output_file is specified.

    Args:
        target_dir (Path):
            The directory path to scan.
        include_extensions (List[str], optional):
            File extensions to include content for (e.g., [".py", ".txt"]).
        skip_hidden (bool):
            Whether to skip hidden files/directories.
        max_size (int, optional):
            Maximum file size (in bytes) to read. If None, no limit is enforced.
        show_metadata (bool):
            If True, include file metadata.
        detect_language (bool):
            If True, attempt to detect code language based on file extension.
        output_format (str):
            Output format: "text" or "json". Default is "text".
        output_file (Path, optional):
            If provided, the resulting output will be written to this file
            instead of being returned.

    Returns:
        Union[List[str], str]:
            - If output_format="text" and output_file is None, returns a list of lines.
            - If output_format="json" and output_file is None, returns a JSON string.
            - If output_file is specified, the function writes to that file and
              returns an empty string or list (depending on the format) for convenience.
    """
    tree = scan_directory(
        target_dir=target_dir,
        include_extensions=include_extensions,
        skip_hidden=skip_hidden,
        max_size=max_size,
        show_metadata=show_metadata,
        detect_language=detect_language
    )

    if output_format not in ["text", "json"]:
        raise ValueError("Invalid output format. Choose 'text' or 'json'.")

    # Build output (text or json)
    if output_format == "text":
        output_data = build_text_output(tree, indent_level=0)  # list of strings
    else:
        output_data = json.dumps(tree, indent=2)  # JSON string

    # If an output_file is specified, write the data and return an empty list/string
    if output_file is not None:
        if output_format == "text":
            # Join lines with newline
            text_content = "\n".join(output_data)
            output_file.write_text(text_content, encoding="utf-8")
            return []
        else:
            # JSON string
            output_file.write_text(output_data, encoding="utf-8")
            return ""
    else:
        # Return the data directly
        return output_data


def main():
    """
    CLI entry point for DirScribe. Parses command-line arguments
    and prints or writes the directory structure.
    """
    parser = argparse.ArgumentParser(
        description="DirScribe: Export a directory structure in text or JSON format, with optional file content."
    )
    parser.add_argument("directory", type=str, help="Path to the directory to scan.")
    parser.add_argument(
        "-e", "--extensions", nargs="*", default=[],
        help="List of file extensions to include content for (e.g. -e .py .txt)."
    )
    parser.add_argument(
        "--skip-hidden", action="store_true",
        help="Skip hidden files and directories."
    )
    parser.add_argument(
        "--max-size", type=int, default=None,
        help="Maximum file size (bytes) to read. Larger files will be skipped."
    )
    parser.add_argument(
        "--show-metadata", action="store_true",
        help="Include file metadata (size, modified time) in the output."
    )
    parser.add_argument(
        "--detect-language", action="store_true",
        help="Attach a 'language' field based on file extension (e.g., '.py' -> 'Python')."
    )
    parser.add_argument(
        "--output-format", choices=["text", "json"], default="text",
        help="Choose output format: 'text' or 'json'. Default is 'text'."
    )
    parser.add_argument(
        "--output-file", type=str, default=None,
        help="If specified, write the output to this file instead of stdout."
    )

    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    output_file = Path(args.output_file).resolve() if args.output_file else None

    result = export_directory_structure(
        target_dir=directory,
        include_extensions=args.extensions,
        skip_hidden=args.skip_hidden,
        max_size=args.max_size,
        show_metadata=args.show_metadata,
        detect_language=args.detect_language,
        output_format=args.output_format,
        output_file=output_file
    )

    # If output_file was specified, nothing is printed to stdout (by design).
    # Otherwise, print the result to stdout.
    if not output_file:
        if args.output_format == "text":
            # 'result' is a list of lines
            for line in result:  # type: ignore
                print(line)
        else:
            # 'result' is a JSON string
            print(result)  # type: ignore


def _read_file_content(file_path: Path) -> str:
    """
    Safely reads text content from a file using UTF-8 (replace errors).

    Args:
        file_path (Path):
            Path object for the file to read.

    Returns:
        str:
            The file's text content (with unknown chars replaced).
    """
    try:
        return file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"<<Error reading file: {e}>>"


def _get_file_metadata(file_path: Path) -> Dict[str, Union[int, str]]:
    """
    Retrieves basic metadata: file size in bytes, last modified time in ISO format.

    Args:
        file_path (Path):
            Path object to the file.

    Returns:
        Dict[str, Union[int, str]]:
            A dictionary containing file size and modified timestamp (ISO).
    """
    size = file_path.stat().st_size
    mtime = file_path.stat().st_mtime
    modified_iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(mtime))
    return {
        "size": size,
        "modified": modified_iso
    }


if __name__ == "__main__":
    main()
