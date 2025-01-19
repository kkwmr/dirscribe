# Contributing to DirScribe

Thank you for your interest in contributing to DirScribe! This document explains how to submit pull requests (PRs), report issues, and follow best practices for a smooth contribution process.

## Development Setup

1. **Fork** the repository on GitHub, then clone it locally.
2. Create a feature branch:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```
3. Install and test the package:
   ```bash
   pip install -e .[dev]
   pytest
   ```

## Coding Style

* Adhere to PEP 8 for Python code style whenever possible.
* Write clear docstrings or comments to help others understand your code.

## Commit Messages

* Keep commit messages concise but descriptive.
* Make incremental commits that each address a single topic or issue if possible.

## Pull Requests

1. Verify that all tests pass and your changes are documented.
2. Open a PR against the `main` branch with a clear title and description.
3. In the PR body, describe what changes you made and why. Include any relevant issue numbers.
4. Be prepared to address review feedback; update your branch with additional commits as needed.

## Issue Reporting

* Use GitHub Issues for bug reports, feature requests, or questions.
* Provide as much detail as possible, including steps to reproduce bugs if applicable.

## License

* DirScribe is distributed under the MIT License.
* Any contributions you make will also fall under that same license.

Thank you for your contributions and support!