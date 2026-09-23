#!/usr/bin/env bash

set -euo pipefail
# Wraps the output of get_metadata_from_anemoi.py into a local_artifacts.json-style file.
# An optional override JSON file can be supplied to patch fields the extraction script
# got wrong or couldn't infer; it is deep-merged on top of the extracted entry.
#
# Usage:
#   ./wrap_artifact_json.sh <artifact_entry.json> <artifact_key> [override.json] [display_name]
#
# Example:
#   ./wrap_artifact_json.sh out.json graceful-gazelle-step10000 override.json "Local test models"

CHECKPOINT="$1"
ARTIFACT_KEY="${2:-graceful-gazelle-step10000}"
OVERRIDE_JSON="${3:-override.json}"
DISPLAY_NAME="${4:-Local test models}"

if [ -n "$OVERRIDE_JSON" ]; then
  OVERRIDE_CONTENT=$(cat "$OVERRIDE_JSON")
else
  OVERRIDE_CONTENT='{}'
fi

ENTRY_JSON=$(mktemp)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
uv run "$SCRIPT_DIR/../backend/packages/fiab-plugin-ecmwf/scripts/get_metadata_from_anemoi.py" "$CHECKPOINT" > "$ENTRY_JSON"

export CONFIG_LOCATION="$SCRIPT_DIR/graceful_gazelle.json"
CHECKPOINT_URL="file://$(realpath "$CHECKPOINT")"

jq -n \
  --arg display_name "$DISPLAY_NAME" \
  --arg key "$ARTIFACT_KEY" \
  --arg checkpoint_url "$CHECKPOINT_URL" \
  --slurpfile entry "$ENTRY_JSON" \
  --argjson override "$OVERRIDE_CONTENT" \
  '{display_name: $display_name, artifacts: {($key): ($entry[0] * $override * {common: {url: $checkpoint_url}})}}' \
  > "$CONFIG_LOCATION"

# cat "$SCRIPT_DIR/config.toml.template" | envsubst > "$SCRIPT_DIR/config.toml"
envsubst '$CONFIG_LOCATION' < config.toml.template > "$SCRIPT_DIR/config.toml"

echo "Created $(realpath --relative-to="$PWD" "$CONFIG_LOCATION") and $(realpath --relative-to="$PWD" "$SCRIPT_DIR/config.toml")"
echo "Copy config.toml to backend/.fiab to enable"
