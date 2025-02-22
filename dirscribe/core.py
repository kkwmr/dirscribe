#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import time
import sys
from pathlib import Path
from typing import List, Optional, Union, Dict, Any

try:
    import pyperclip
except ImportError:
    pyperclip = None

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
    detect_language: bool = False,
    exclude_extensions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Recursively scans the target directory and builds a nested dictionary
    representing directories and files. File contents are included only for
    certain extensions if specified.

    Args:
        target_dir (Path):
            The directory path to scan.
        include_extensions (List[str], optional):
            A list of file extensions to include content for. If None, all files are included.
            If an empty list, no file content is included.
        skip_hidden (bool):
            If True, hidden files and directories (names starting with '.') are skipped.
        max_size (int, optional):
            Maximum file size in bytes to read. Files larger than this are skipped.
        show_metadata (bool):
            If True, file metadata (size, modified time) is included in the output.
        detect_language (bool):
            If True, a "language" field is added to each file based on extension.
        exclude_extensions (List[str], optional):
            A list of file extensions to exclude from the output entirely.

    Returns:
        Dict[str, Any]: A nested dictionary describing the directory structure.
    """
    if exclude_extensions is None:
        exclude_extensions = []

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
        if skip_hidden and entry.name.startswith('.'):
            continue

        if entry.is_dir():
            subtree = scan_directory(
                entry,
                include_extensions=include_extensions,
                skip_hidden=skip_hidden,
                max_size=max_size,
                show_metadata=show_metadata,
                detect_language=detect_language,
                exclude_extensions=exclude_extensions
            )
            tree["children"].append(subtree)
        else:
            if entry.suffix.lower() in [ext.lower() for ext in exclude_extensions]:
                continue

            file_node = {
                "type": "file",
                "name": entry.name,
                "path": str(entry.resolve())
            }

            if detect_language:
                lang = LANGUAGE_MAP.get(entry.suffix.lower())
                if lang:
                    file_node["language"] = lang

            if show_metadata:
                file_node["metadata"] = _get_file_metadata(entry)

            if include_extensions and len(include_extensions) > 0:
                if "ALL_MODE" in include_extensions:
                    should_include = True
                else:
                    should_include = (entry.suffix.lower() in [ext.lower() for ext in include_extensions])
            elif include_extensions is None:
                should_include = True
            else:
                should_include = False

            if should_include:
                size = entry.stat().st_size
                if max_size is not None and size > max_size:
                    file_node["content"] = f"<<File size exceeds {max_size} bytes, skipping content>>"
                else:
                    file_node["content"] = _read_file_content(entry)

            tree["children"].append(file_node)

    return tree


def build_text_output(tree: Dict[str, Any], indent_level: int = 0) -> List[str]:
    """
    Builds a list of text lines (ASCII tree style) from the nested dictionary.

    Args:
        tree (Dict[str, Any]): The directory structure dictionary returned by scan_directory().
        indent_level (int): Internal parameter for managing indentation in recursion.

    Returns:
        List[str]: A list of text lines representing the directory tree and optional contents.
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
    output_file: Optional[Path] = None,
    exclude_extensions: Optional[List[str]] = None
) -> Union[List[str], str]:
    """
    Scans the directory and produces output in either text or JSON format.
    Optionally writes the result to a file if output_file is specified.

    Args:
        target_dir (Path): The directory to scan.
        include_extensions (List[str], optional): File extensions to include contents for.
            If None, includes all. If empty, includes none.
        skip_hidden (bool): Whether to skip hidden files/directories.
        max_size (int, optional): Maximum file size in bytes to read. Larger files are skipped.
        show_metadata (bool): Whether to include file metadata in the output.
        detect_language (bool): Whether to add a 'language' field based on file extension.
        output_format (str): 'text' or 'json'. Default is 'text'.
        output_file (Path, optional): If specified, the output is written to this file.
        exclude_extensions (List[str], optional): File extensions to exclude entirely.

    Returns:
        Union[List[str], str]:
            - If output_format='text' and output_file is None, returns a list of lines.
            - If output_format='json' and output_file is None, returns a JSON string.
            - If output_file is specified, writes to file and returns an empty list or string.
    """
    tree = scan_directory(
        target_dir=target_dir,
        include_extensions=include_extensions,
        skip_hidden=skip_hidden,
        max_size=max_size,
        show_metadata=show_metadata,
        detect_language=detect_language,
        exclude_extensions=exclude_extensions
    )

    if output_format not in ["text", "json"]:
        raise ValueError("Invalid output format. Choose 'text' or 'json'.")

    if output_format == "text":
        output_data = build_text_output(tree)
    else:
        output_data = json.dumps(tree, indent=2)

    if output_file is not None:
        if output_format == "text":
            text_content = "\n".join(output_data)
            output_file.write_text(text_content, encoding="utf-8")
            return []
        else:
            output_file.write_text(output_data, encoding="utf-8")
            return ""
    else:
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
        help=(
            "List of file extensions to include content for (e.g. -e .py .txt). "
            "If '-e' or '--extensions' is passed with no arguments, all file contents will be included."
        )
    )
    parser.add_argument(
        "-x", "--exclude-extensions", nargs="*", default=[],
        help="List of file extensions to exclude from the output entirely."
    )
    parser.add_argument(
        "--skip-hidden", action="store_true",
        help="Skip hidden files and directories."
    )
    parser.add_argument(
        "--max-size", type=int, default=None,
        help="Maximum file size (in bytes) to read. Larger files will be skipped."
    )
    parser.add_argument(
        "--show-metadata", action="store_true",
        help="Include file metadata (size, modified time) in the output."
    )
    parser.add_argument(
        "--detect-language", action="store_true",
        help="Attach a 'language' field based on file extension."
    )
    parser.add_argument(
        "--output-format", choices=["text", "json"], default="text",
        help="Choose output format: 'text' or 'json'. Default is 'text'."
    )
    parser.add_argument(
        "--output-file", type=str, default=None,
        help="If specified, write the output to this file instead of stdout."
    )
    parser.add_argument(
        "--clip", action="store_true",
        help="Copy the output to the clipboard (requires pyperclip)."
    )

    args = parser.parse_args()
    directory = Path(args.directory).resolve()

    use_all_extensions = False
    if (("-e" in sys.argv) or ("--extensions" in sys.argv)) and len(args.extensions) == 0:
        use_all_extensions = True

    if use_all_extensions:
        include_exts = None
    else:
        include_exts = args.extensions

    output_file = Path(args.output_file).resolve() if args.output_file else None

    result = export_directory_structure(
        target_dir=directory,
        include_extensions=include_exts,
        skip_hidden=args.skip_hidden,
        max_size=args.max_size,
        show_metadata=args.show_metadata,
        detect_language=args.detect_language,
        output_format=args.output_format,
        output_file=output_file,
        exclude_extensions=args.exclude_extensions
    )

    if args.clip:
        if pyperclip is None:
            print("[ERROR] Cannot copy to clipboard because 'pyperclip' is not installed.")
        else:
            if args.output_format == "text":
                if isinstance(result, list):
                    text_output = "\n".join(result)
                else:
                    text_output = "\n".join(result) if result else ""
                pyperclip.copy(text_output)
            else:
                json_output = result if isinstance(result, str) else ""
                pyperclip.copy(json_output)

    if not output_file:
        if args.output_format == "text":
            for line in result:  # type: ignore
                print(line)
        else:
            print(result)  # type: ignore


def _read_file_content(file_path: Path) -> str:
    """
    Safely reads text content from the specified file using UTF-8 with error replacement.
    """
    try:
        return file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"<<Error reading file: {e}>>"


def _get_file_metadata(file_path: Path) -> Dict[str, Union[int, str]]:
    """
    Retrieves basic metadata: file size in bytes and last modified time in ISO format.
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
