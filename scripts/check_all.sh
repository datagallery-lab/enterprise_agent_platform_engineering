#!/usr/bin/env bash
# Run all v0.1 quality gates locally.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== chapter template check ==="
python3 scripts/check_chapter_template.py

echo
echo "=== figure and table numbering check ==="
python3 scripts/check_figures_tables.py

echo
echo "=== markdown table render check ==="
python3 scripts/check_markdown_tables.py

echo
echo "=== citation style check ==="
python3 scripts/check_citation_style.py

echo
echo "=== tone and template phrase check ==="
python3 scripts/check_tone.py

echo
echo "=== image size check ==="
python3 scripts/check_image_sizes.py --root docs/images/part1
python3 scripts/check_image_sizes.py --root docs/images/part2
python3 scripts/check_image_sizes.py --root docs/images/part3
python3 scripts/check_image_sizes.py --root docs/images/part4
python3 scripts/check_image_sizes.py --root docs/images/part5
python3 scripts/check_image_sizes.py --root docs/images/part6
python3 scripts/check_image_sizes.py --root docs/images/part7
python3 scripts/check_image_sizes.py --root docs/images/part8
python3 scripts/check_image_sizes.py --root docs/images/part9
python3 scripts/check_image_sizes.py --root docs/images/part10
python3 scripts/check_image_sizes.py --root docs/images/part11

echo
echo "=== glossary acronym check ==="
python3 scripts/check_glossary.py

echo
echo "=== sensitive info scan ==="
python3 scripts/check_sensitive.py

echo
echo "=== mini-platform tests ==="
cd mini-platform
python3 -m pytest tests/ -q
cd "$ROOT"

echo
echo "✓ all Chinese first-version quality gates passed."
