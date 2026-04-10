#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
if [ ! -d "PriceCompass" ]; then
    git clone -b index https://github.com/nlevi-dev/PriceCompass index
fi
cd ..
cd frontend
npm run build
cp dist/index.html ../deploy/index/index.html
