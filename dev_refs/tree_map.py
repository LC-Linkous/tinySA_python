#!/usr/bin/env python3
"""Generate an ASCII file tree of the python project."""

import os
import sys
from pathlib import Path

EXCLUDE_DIRS = {
    '.git', '__pycache__', '.pytest_cache', '.venv',
    'node_modules', '.mypy_cache', '.ruff_cache',
}
EXCLUDE_FILES = {
    '.DS_Store', 'Thumbs.db',
}
EXCLUDE_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd',
}

def build_tree(path: Path, prefix: str = '', is_last: bool = True) -> list[str]:
    lines = []
    connector = '└── ' if is_last else '├── '
    lines.append(f'{prefix}{connector}{path.name}')

    if path.is_dir():
        extension = '    ' if is_last else '│   '
        children = sorted(
            [c for c in path.iterdir()
             if c.name not in EXCLUDE_DIRS
             and c.name not in EXCLUDE_FILES
             and c.suffix not in EXCLUDE_EXTENSIONS],
            key=lambda p: (p.is_file(), p.name.lower())
        )
        for i, child in enumerate(children):
            is_child_last = (i == len(children) - 1)
            lines.extend(build_tree(child, prefix + extension, is_child_last))

    return lines


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    root = root.resolve()

    if not root.exists():
        print(f'Error: path not found: {root}')
        sys.exit(1)

    lines = [str(root.name) + '/']
    children = sorted(
        [c for c in root.iterdir()
         if c.name not in EXCLUDE_DIRS
         and c.name not in EXCLUDE_FILES
         and c.suffix not in EXCLUDE_EXTENSIONS],
        key=lambda p: (p.is_file(), p.name.lower())
    )
    for i, child in enumerate(children):
        lines.extend(build_tree(child, '', i == len(children) - 1))

    output = '\n'.join(lines)
    out_path = root / 'project-tree.txt'
    out_path.write_text(output + '\n', encoding='utf-8')

    print(output)
    print(f'\n✓ Saved to {out_path}')


if __name__ == '__main__':
    main()