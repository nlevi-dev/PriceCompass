#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
cd ..
python scrape.py
pytest test.py
latest_json=$(find data -name "*.json" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
if [ -n "$latest_json" ]; then
    cp "$latest_json" frontend/src/data.json
fi
