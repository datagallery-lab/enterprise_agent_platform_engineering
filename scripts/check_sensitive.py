"""Scan all docs and mini-platform code for sensitive patterns.

v0.1 minimal patterns:
- AWS Access Key (AKIA...)
- generic API key patterns ("sk-..." OpenAI-style)
- private IP / internal hosts (10.x, 192.168.x, .internal)
- real company names blocked list (extensible, default empty)
- email addresses

Usage:
    python scripts/check_sensitive.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "docs", ROOT / "mini-platform"]

PATTERNS = {
    "AWS_ACCESS_KEY": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "OPENAI_KEY": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "ANTHROPIC_KEY": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    "PRIVATE_IP_10": re.compile(r"\b10\.(?:\d{1,3}\.){2}\d{1,3}\b"),
    "PRIVATE_IP_192": re.compile(r"\b192\.168\.\d{1,3}\.\d{1,3}\b"),
    "INTERNAL_HOST": re.compile(r"\b[a-z0-9-]+\.internal\b"),
    "EMAIL": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"),
}

EMAIL_ALLOWLIST = {
    "noreply@anthropic.com",
}

INTERNAL_HOST_ALLOWLIST = {
    "history.internal",  # Debezium schema.history.internal.* config key
}

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", "site"}


def iter_files() -> list[Path]:
    out: list[Path] = []
    for base in TARGETS:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_dir():
                continue
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if p.suffix not in {".md", ".py", ".yaml", ".yml", ".toml", ".json", ".txt", ".sh"}:
                continue
            out.append(p)
    return out


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    hits: list[tuple[int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return hits
    for i, line in enumerate(text.splitlines(), start=1):
        for name, pat in PATTERNS.items():
            for m in pat.finditer(line):
                if name == "EMAIL" and m.group(0) in EMAIL_ALLOWLIST:
                    continue
                if name == "INTERNAL_HOST" and m.group(0) in INTERNAL_HOST_ALLOWLIST:
                    continue
                hits.append((i, name, m.group(0)))
    return hits


def main() -> int:
    failures = 0
    for path in iter_files():
        hits = scan_file(path)
        if hits:
            failures += 1
            rel = path.relative_to(ROOT)
            print(f"✗ {rel}")
            for line_no, name, match in hits[:5]:
                print(f"   line {line_no}: {name} -> {match!r}")
            if len(hits) > 5:
                print(f"   ... and {len(hits) - 5} more")
    if failures:
        print(f"\n{failures} file(s) contain sensitive patterns.")
        return 1
    print("✓ sensitive scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
