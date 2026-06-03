#!/usr/bin/env bash
# Run all v0.1 quality gates locally.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== chapter template check ==="
python3 scripts/check_chapter_template.py

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
echo "✓ all v0.1 quality gates passed."
