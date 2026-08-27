from __future__ import annotations

import re
import sys
from pathlib import Path

IGNORED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
PATTERNS = [
    re.compile(r"gh[opsru]_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (RSA |OPENSSH |EC |DSA |)?PRIVATE KEY-----"),
    re.compile(r"sb_secret_[A-Za-z0-9_-]+"),
]


def should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def main() -> int:
    hits: list[str] = []
    for path in Path(".").rglob("*"):
        if should_skip(path) or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(pattern.search(text) for pattern in PATTERNS):
            hits.append(str(path))

    if hits:
        print("potential secret patterns found:", file=sys.stderr)
        print("\n".join(hits), file=sys.stderr)
        return 1

    print("secret scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
