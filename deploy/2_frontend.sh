#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
cd ..
python deploy/compress/compress.py
cd frontend
npm run build
cp dist/index.html ../deploy/index/index.html
