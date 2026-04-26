#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
cd index
git reset --soft 87c2985c3c268fa0ad30838ae425531c011ddc79
git add -A
git commit -m sync
git push origin -f index
cd ../..
git add deploy/index
git commit -m sync
git push origin master