# DirScribe — Explore, Document, and Share Your Directory Structures

![Version](https://img.shields.io/badge/version-0.1.2-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python 3.7+](https://img.shields.io/badge/Python-3.7+-brightgreen.svg)
![Stars](https://img.shields.io/github/stars/kkwmr/dirscribe?style=social)
[![Total Downloads](https://pepy.tech/badge/dirscribe)](https://pepy.tech/project/dirscribe)

DirScribe is a **lightweight yet powerful** CLI tool and Python library for **exporting directory structures** in either **text** or **JSON** format. It helps you **optionally** include file contents, **detect programming languages**, skip hidden items, limit file reading by size, show metadata (size and modification time), and output results directly to your terminal or a file.

> Created by: [Kazuki Kawamura](https://casp.jp) (Caspy /ˈkæspi/, かすぴー)  
> **License:** [MIT License](./LICENSE)

## Quick Look

One of DirScribe's key features is how easily it can include file contents by extension.  
- If you run `dirscribe /path -e .py .txt`, it includes only `.py` and `.txt` files' contents.  
- **If you run `dirscribe /path -e` with no arguments, it includes *all* file contents** (new in v0.1.2).  
- If you omit `-e` entirely, no file contents are included—just the directory tree.

Another new feature in v0.1.2 is `--clip`, which copies the final output (text or JSON) to your clipboard for quick sharing.

**Example**:
```bash
dirscribe /path/to/your_project -e .py --clip
```

This command shows all .py file contents (skipping other extensions) and copies the result to your clipboard.

Below is a quick text-based preview if you scan a sample project:

```
📁 your_project/
  📄 main.py (Python)
    def calculate_total(items):
        return sum(item.price for item in items)
    
    def main():
        print("Processing orders...")
  
  📁 templates/
    📄 index.html (HTML)
      <!DOCTYPE html>
      <html>
        <head><title>My App</title></head>
        <body><h1>Welcome</h1></body>
      </html>
    
    📄 style.css (CSS)
      body {
        margin: 0;
        padding: 20px;
        font-family: sans-serif;
      }
```

If you prefer JSON:

```bash
dirscribe /path/to/your_project --output-format json
```

You get:

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
- Key Features
- Why DirScribe?
- Installation
- Quick Start
- Command-Line Usage
- Python Library Usage
- Use Cases
- AI Tools Integration
- Contributing
- License

## Key Features

- Text or JSON Output
  - Choose between a human-readable tree format or a structured JSON representation for advanced integrations.

- File Content Inclusion
  - Display the contents of files for specific extensions (e.g., .py, .js, .txt).
  - Tip: With v0.1.2, if you add `-e` with no extensions, all file contents are included.

- Language Detection
  - Show the programming language name (e.g., .py -> Python) alongside file names.

- Skip Hidden
  - Omit hidden files and directories (names starting with a dot).

- Maximum Size Limit
  - Automatically skip file content if a file exceeds a specified byte-size.

- Metadata Display
  - Show file size and last modification timestamp in the output.

- Clipboard Copy
  - Use `--clip` to copy the output directly to your clipboard (requires pyperclip).

- Save to File
  - Output can be redirected to a file rather than just printing to the console.

- Highly Configurable
  - Combine various options to fit your exact needs.

## Why DirScribe?

- Instant Documentation
  - Quickly generate a snapshot of your codebase – perfect for onboarding new team members or archiving project structures.

- Efficient Code Reviews
  - Include file contents up to a specified size, letting you skim important files without diving deeply into each folder.

- Language Insights
  - Recognize the languages used in your project at a glance.

- Scriptable
  - Integrate DirScribe into CI/CD pipelines or other automated workflows to maintain updated structure maps.

- Open Source & Community-Driven
  - MIT-licensed, easily extended, and continuously improved by the community.

## Installation

You can install DirScribe by cloning the repository and running:

```bash
pip install .
```

If you're actively editing the source, you might prefer:

```bash
pip install -e .
```

This sets up DirScribe in "editable" mode so changes in the code take immediate effect.

If DirScribe is published on PyPI in the future, you'll be able to do:

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

Include all file contents (no matter the extension):

```bash
dirscribe /path/to/project -e
```

Copy the result to your clipboard (also new in 0.1.2):

```bash
dirscribe /path/to/project --clip
```

That's it! Mix and match the options below for your needs.

## Command-Line Usage

Once installed, you can run dirscribe:

```
dirscribe [DIRECTORY] [OPTIONS]
```

### Common Options

- `-e, --extensions <EXT ...>`
  - Specify which file extensions to include content for (e.g., `-e .py .js`).
  - If you pass `-e` with no extensions, DirScribe will include the contents of all files.
  - If you omit `-e` entirely, it includes no file contents.

- `--detect-language`
  - Enables language detection based on file extensions (e.g., .py -> Python).

- `--skip-hidden`
  - Skips files and directories whose names begin with `.`.

- `--max-size <BYTES>`
  - Maximum file size (in bytes) to read. Files larger than this are ignored.

- `--show-metadata`
  - Displays file metadata (size in bytes, last modification time) next to file content.

- `--output-format <text|json>`
  - Output either a text-based tree or JSON structure. Defaults to text.

- `--output-file <FILE>`
  - Write the output to the specified file instead of printing to stdout.

- `--clip`
  - Copy the final output to your clipboard (requires pyperclip).

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

What this does:
1. Recursively scans `/path/to/src`
2. Shows contents of files with .py or .html extension (up to 2000 bytes)
3. Skips hidden items (names starting with a dot)
4. Displays file size & last modified time
5. Identifies language names where possible
6. Renders as a textual tree
7. Saves it to output.txt (instead of printing to the terminal)

## Python Library Usage

DirScribe can also be used as a library:

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
        output_file=None
    )
    
    # If output_format="text" and output_file=None, you get a list of lines
    for line in lines:
        print(line)

if __name__ == "__main__":
    main()
```

### Parameters

- `target_dir` (Path)
  - The folder you want to scan.

- `include_extensions` (List[str], optional)
  - File extensions for which file contents should be included.
  - Pass None or use `-e` with no args to include all files.

- `skip_hidden` (bool, default=False)
  - Skip hidden files and directories.

- `max_size` (int, optional)
  - Skip content for files larger than this size.

- `show_metadata` (bool, default=False)
  - Show file size and last modification time.

- `detect_language` (bool, default=False)
  - Attach a language field based on file extension (e.g., .py -> Python).

- `output_format` (str, default="text")
  - Either "text" or "json".

- `output_file` (Path, optional)
  - If provided, the data is written to that file. Returns empty list/string.

### Return Values:

- If `output_format="text"` and `output_file=None`, returns a list of text lines.
- If `output_format="json"` and `output_file=None`, returns a JSON string.
- If `output_file` is set, writes to that file and returns an empty list or empty string.

## Use Cases

### Instant Project Documentation
Generate a tree-like structure of your source code, optionally with file contents.
Great for sharing with collaborators or creating "at-a-glance" docs.

### Code Review & Auditing
Quickly see which files exist, their languages, and read short/medium files directly.

### Security / Compliance Checks
Skip hidden or large files, or selectively scan certain file types.

### CI/CD Integration
Save a JSON manifest of your repository structure as part of your build artifacts.
Compare structure between builds or track changes over time.

### Scripting / Automation
Leverage DirScribe's JSON or text output in custom pipelines or scripts.

## AI Tools Integration

DirScribe's output is perfect for feeding into ChatGPT or other AI tools to analyze or summarize a project's structure:

1. Generate a text or JSON snapshot:
```bash
dirscribe /path/to/src --output-format text > structure.txt
```

2. Copy/paste structure.txt into ChatGPT (or your AI tool).

3. Ask questions like:
   - "Give me an overview of this project."
   - "Identify potential security concerns."
   - "Suggest improvements or refactoring ideas."

By providing AI with a precise structure (and optionally file contents), you can quickly gain insights or documentation without manual exploration.

## Contributing

We welcome contributions, suggestions, and bug reports! See our CONTRIBUTING.md to learn how to propose changes or open pull requests. We also encourage you to open an issue for any problems or feature requests.

Ways to help:
- Code contributions (new features, bug fixes, refactoring)
- Documentation improvements (clarify instructions, add examples)
- Language mapping expansions (add more file extensions to LANGUAGE_MAP)
- Feedback and testing on different OS environments or large-scale projects

If you find DirScribe valuable, please star the repository and share it with fellow developers!

## License

This project is distributed under the MIT License.
© 2025 Kazuki Kawamura