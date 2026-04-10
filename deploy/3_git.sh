#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
cd index
git reset --soft c70efcabfbbe624a4647eb58c534277d9888da0a
git add -A
git commit -m index
git push origin -f index
