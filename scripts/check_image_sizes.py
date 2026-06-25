#!/usr/bin/env python3
"""Fail when documentation images exceed a per-file size budget."""
from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_LIMIT_MB = 5
DEFAULT_ROOT = Path("docs/images")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check documentation image sizes.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--limit-mb", type=float, default=DEFAULT_LIMIT_MB)
    parser.add_argument("--total-budget-mb", type=float, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    limit_bytes = int(args.limit_mb * 1024 * 1024)
    extensions = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

    oversized: list[tuple[Path, int]] = []
    total_bytes = 0
    image_count = 0
    for path in sorted(args.root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
        size = path.stat().st_size
        total_bytes += size
        image_count += 1
        if size > limit_bytes:
            oversized.append((path, size))

    if oversized:
        print(f"Per-image check failed: {len(oversized)} image(s) larger than {args.limit_mb:g} MB.")
        for path, size in oversized:
            print(f"- {path}: {size / 1024 / 1024:.2f} MB")
        return 1

    print(f"Per-image check passed: {image_count} image(s) <= {args.limit_mb:g} MB.")

    if args.total_budget_mb is not None:
        total_mb = total_bytes / 1024 / 1024
        if total_mb > args.total_budget_mb:
            print(f"Total budget failed: {total_mb:.2f} MB > {args.total_budget_mb:g} MB.")
            return 1
        print(f"Total budget passed: {total_mb:.2f} MB <= {args.total_budget_mb:g} MB.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
