#!/usr/bin/env bash

set -euo pipefail

mbtiles_dir="${1:-mbtiles}"
shopt -s nullglob
files=("$mbtiles_dir"/*.mbtiles)

if [[ ${#files[@]} -eq 0 ]]; then
    printf 'No s’han trobat fitxers MBTiles a %s\n' "$mbtiles_dir"
    exit 0
fi

for file in "${files[@]}"; do
    printf '\n=== %s ===\n' "$file"
    sqlite3 "$file" 'SELECT name, value FROM metadata ORDER BY name;'
done
