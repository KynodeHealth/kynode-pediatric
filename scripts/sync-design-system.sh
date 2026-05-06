#!/usr/bin/env bash
# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.
#
# Sync the design-system foundation files from the local-node app into the
# static demo so both surfaces share the same tokens, theme bootstrap, icon
# library and font.
#
# Run after editing any of:
#   apps/local-node/src/kynode_pediatric_local_node/static/tokens.css
#   apps/local-node/src/kynode_pediatric_local_node/static/theme-bootstrap.js
#   apps/local-node/src/kynode_pediatric_local_node/static/icons.js
#   apps/local-node/src/kynode_pediatric_local_node/static/fonts/InterVariable.woff2
#
# Usage: bash scripts/sync-design-system.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO_ROOT/apps/local-node/src/kynode_pediatric_local_node/static"
DST="$REPO_ROOT/demo/static"

if [ ! -d "$SRC" ]; then
  echo "✗ Source directory not found: $SRC" >&2
  exit 1
fi

if [ ! -d "$DST" ]; then
  echo "✗ Destination directory not found: $DST" >&2
  exit 1
fi

mkdir -p "$DST/fonts"

declare -a FILES=(
  "tokens.css"
  "theme-bootstrap.js"
  "icons.js"
  "fonts/InterVariable.woff2"
)

CHANGED=0
for path in "${FILES[@]}"; do
  src_file="$SRC/$path"
  dst_file="$DST/$path"
  if [ ! -f "$src_file" ]; then
    echo "✗ Missing source: $src_file" >&2
    exit 1
  fi
  if ! cmp -s "$src_file" "$dst_file" 2>/dev/null; then
    cp "$src_file" "$dst_file"
    echo "  → updated $path"
    CHANGED=$((CHANGED + 1))
  fi
done

if [ "$CHANGED" -eq 0 ]; then
  echo "✓ Demo design system already in sync — nothing to do."
else
  echo ""
  echo "✓ Synced $CHANGED file(s) from local-node into demo/static/"
  echo ""
  echo "Reminder: commit the changes in demo/static/ alongside the local-node"
  echo "          changes so the public demo and the app stay visually identical."
fi
