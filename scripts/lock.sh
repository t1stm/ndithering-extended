#!/bin/bash
cd "$(dirname "$0")/.."
uv sync
uv export -o pylock.toml > /dev/null
uv export -o requirements.txt --no-annotate --no-hashes > /dev/null
