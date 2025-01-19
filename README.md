# DirScribe — Explore, Document, and Share Your Directory Structures

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-3.7+-brightgreen.svg" alt="Python 3.7+">
  <img src="https://img.shields.io/github/stars/kkwmr/dirscribe?style=social" alt="Stars">
</p>

DirScribe is a **lightweight yet powerful** CLI tool and Python library for **exporting directory structures** in either **text** or **JSON** format. It helps you **optionally** include file contents, **detect programming languages**, skip hidden items, limit file reading by size, show metadata (size and modification time), and output results directly to your terminal or a file.

> Created by: [Kazuki Kawamura](https://casp.jp) (Caspy /ˈkæspi/, かすぴー)  
> **License:** [MIT License](./LICENSE)

## Quick Look

If you run:

```bash
dirscribe /path/to/your_project
```

You'll see a text-based tree of your directory structure with file contents (example below):

```
📁 your_project/
  📄 main.py (Python)
  ├─ Content:
  │  def calculate_total(items):
  │      return sum(item.price for item in items)
  │  
  │  def main():
  │      print("Processing orders...")
  │  
  📁 templates/
    📄 index.html (HTML)
    ├─ Content:
    │  <!DOCTYPE html>
    │  <html>
    │    <head><title>My App</title></head>
    │    <body><h1>Welcome</h1></body>
    │  </html>
    │
    📄 style.css (CSS)
    ├─ Content:
    │  body {
    │    margin: 0;
    │    padding: 20px;
    │    font-family: sans-serif;
    │  }
```

Or, if you prefer JSON:

```bash
dirscribe /path/to/your_project --output-format json
```

You get a structured JSON representation:

```json
{
  "type": "directory",
  "name": "your_project",
  "path": "absolute/path/your_project",
  "children": [
    {
      "type": "file",
      "name": "main.py",
      "path": "...",
      "language": "Python",
      "content": "...",
      ...
    },
    ...
  ]
}
```

## Table of Contents
1. [Key Features](#key-features)
2. [Why DirScribe?](#why-dirscribe)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Command-Line Usage](#command-line-usage)
6. [Python Library Usage](#python-library-usage)
7. [Use Cases](#use-cases)
8. [AI Tools Integration](#ai-tools-integration)
9. [Contributing](#contributing)
10. [License](#license)

## Key Features

- **Text or JSON Output**: Choose between a human-readable tree format or a structured JSON representation for advanced integrations.
- **File Content Inclusion**: Display the contents of files for specific extensions (e.g., `.py`, `.js`, `.txt`, etc.).
- **Language Detection**: Show the programming language name (e.g., `.py` -> *Python*) alongside file names.
- **Skip Hidden**: Omit hidden files and directories (those starting with a dot).
- **Maximum Size Limit**: Automatically skip file content if a file exceeds a specified byte-size.
- **Metadata Display**: Show file size and last modification timestamp in the output.
- **Save to File**: Output can be redirected to a file rather than just printing to the console.
- **Highly Configurable**: Combine various options to fit your exact needs.

## Why DirScribe?

- **Instant Documentation**: Quickly generate a snapshot of your codebase – perfect for onboarding new team members or archiving project structures.
- **Efficient Code Reviews**: Include file contents up to a specified size, letting you skim important files without digging into each folder manually.
- **Language Insights**: Recognize the languages used in your project at a glance.
- **Scriptable**: Integrate DirScribe into CI/CD pipelines or other automated workflows to maintain updated structure maps.
- **Open Source & Community-Driven**: MIT-licensed and easy to extend.

## Installation

You can install DirScribe either by cloning this repository or from your own distribution setup:

```bash
# From source (assuming you're in the DirScribe project directory):
pip install .
```

If you're editing the source, you might prefer:

```bash
pip install -e .
```

(This sets up DirScribe in "editable" mode so changes in the code take immediate effect.)

If DirScribe is published on PyPI in the future, you'll be able to run:

```bash
pip install dirscribe
```

directly.

## Quick Start

Generate a text listing of a directory:

```bash
dirscribe /path/to/project
```

Generate a JSON output and save it to a file:

```bash
dirscribe /path/to/project --output-format json --output-file project_structure.json
```

That's it! Customize the output further using the rich set of options explained below.

## Command-Line Usage

Once installed, you can run dirscribe in your terminal:

```bash
dirscribe [DIRECTORY] [OPTIONS]
```

### Common Options

- `-e, --extensions <EXT ...>`  
  Specify which file extensions to include content for (e.g. -e .py .js).

- `--detect-language`  
  Enables language detection based on file extensions.  
  Example: .py -> Python, .js -> JavaScript, etc.

- `--skip-hidden`  
  Skips files and directories whose names begin with `.`

- `--max-size <BYTES>`  
  Maximum file size (in bytes) to read. Files larger than this are ignored (content not shown).

- `--show-metadata`  
  Displays file metadata (size in bytes, last modification time) next to file content.

- `--output-format <text|json>`  
  Output either a text-based tree or JSON structure. Defaults to text.

- `--output-file <FILE>`  
  Write the output to the specified file instead of printing to stdout.

### Example: Combine Multiple Options

```bash
dirscribe /path/to/src \
  -e .py .html \
  --detect-language \
  --skip-hidden \
  --max-size 2000 \
  --show-metadata \
  --output-format text \
  --output-file output.txt
```

What it does:
- Recursively scans `/path/to/src`
- Shows contents of files with `.py` or `.html` extension (up to 2000 bytes)
- Skips hidden items (names starting with .)
- Displays file size & last modified time
- Identifies language names where possible
- Renders as a textual tree
- Saves it to output.txt (instead of printing to the terminal)

## Python Library Usage

DirScribe can also be used as a library in your Python scripts or applications:

```python
from pathlib import Path
from dirscribe.core import export_directory_structure

def main():
    directory = Path("/path/to/src")
    
    # Export directory structure as text (list of lines)
    lines = export_directory_structure(
        target_dir=directory,
        include_extensions=[".py", ".html"],
        skip_hidden=True,
        max_size=2000,
        show_metadata=True,
        detect_language=True,
        output_format="text",
        output_file=None  # if you'd like to write to a file, pass Path("output.txt")
    )
    
    # If output_format="text" and output_file=None, you get a list of lines
    for line in lines:
        print(line)

if __name__ == "__main__":
    main()
```

### Parameters

- `target_dir (Path)`: The folder you want to scan.
- `include_extensions (List[str], optional)`: List of extensions for which file contents should be shown.
- `skip_hidden (bool, default=False)`: Skip hidden files/directories.
- `max_size (int, optional)`: Skip content for files larger than this size.
- `show_metadata (bool, default=False)`: Show size and last modification time.
- `detect_language (bool, default=False)`: Attach a language field based on file extension.
- `output_format (str, default="text")`: Either "text" or "json".
- `output_file (Path, optional)`: If provided, write output to that file.

The function returns:
- A list of strings (text lines) if `output_format="text"` and `output_file=None`, or
- A JSON string if `output_format="json"` and `output_file=None`.
- If `output_file` is set, the data is written to the file, and the function returns an empty list or empty string.

## Use Cases

### Instant Project Documentation
Generate a tree-like structure of your source code, complete with file contents (for specific extensions) and metadata. Ideal for:
- Sharing with collaborators
- Creating "at-a-glance" docs

### Code Review & Auditing
Quickly see which files exist, their languages, and read short/medium files directly without jumping between directories.

### Security / Compliance Checks
Skip hidden or large files, or selectively scan certain file types to ensure they meet certain criteria.

### CI/CD Integration
Save a JSON manifest of your repository structure as part of your build artifacts. Compare structure between builds or track changes over time.

### Scripting / Automation
If you need to parse directory contents in a custom pipeline, DirScribe's Python API and JSON output can be easily integrated.

## AI Tools Integration

DirScribe's output is perfect for feeding into ChatGPT or other AI tools to analyze or summarize a project's structure:

1. Generate a text or JSON snapshot:
```bash
dirscribe /path/to/src --output-format text > structure.txt
```

2. Copy-Paste the contents of `structure.txt` into ChatGPT (or any AI model).

3. Ask the AI:
- "Give me an overview of this project."
- "Identify potential security concerns."
- "Suggest improvements or refactoring ideas."

By providing AI with a precise structure (and optionally file contents), you can quickly gain insights or documentation without manual exploration.

## Contributing

Contributions, suggestions, and bug reports are warmly welcomed! Check out our [CONTRIBUTING.md](./CONTRIBUTING.md) to learn how to propose changes or open pull requests. We also encourage you to open an issue if you encounter problems or have feature requests.

Ways to help:
- Code contributions (new features, bug fixes, refactoring)
- Documentation improvements (clarify instructions, add examples)
- Language mapping expansions (add more file extensions to LANGUAGE_MAP)
- Feedback and testing on different OS environments or large-scale projects

If you find DirScribe valuable, please consider starring the repository and sharing it with your fellow developers!

## License

This project is distributed under the MIT License.
© 2025 Kazuki Kawamura