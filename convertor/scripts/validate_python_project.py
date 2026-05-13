#!/usr/bin/env python3
"""Validate the minimum structure of a generated Python port."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "MIGRATION.md",
    "TODO.md",
    "src/main.py",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.project_root)

    errors = []
    warnings = []

    if not root.exists():
        errors.append(f"Missing project folder: {root}")
    else:
        for rel in REQUIRED_FILES:
            path = root / rel
            if not path.exists():
                errors.append(f"Missing required file: {rel}")
            elif path.is_file() and path.stat().st_size == 0:
                warnings.append(f"Empty required file: {rel}")

        main_py = root / "src" / "main.py"
        if main_py.exists():
            try:
                ast.parse(main_py.read_text(encoding="utf-8", errors="ignore"))
            except SyntaxError as exc:
                errors.append(f"Python syntax error in src/main.py: {exc}")

        todo = root / "TODO.md"
        if todo.exists():
            todo_text = todo.read_text(encoding="utf-8", errors="ignore").lower()
            if "todo" not in todo_text and "high" not in todo_text and "medium" not in todo_text and "low" not in todo_text:
                warnings.append("TODO.md should contain actionable items or explicitly state that none remain.")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1
    print("Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
