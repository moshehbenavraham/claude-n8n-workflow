#!/bin/bash
# list-nodes.sh - Quick utility to list nodes in a split workflow folder
# Usage: ./list-nodes.sh <workflow-folder>

FOLDER="${1:-.}"

if [ ! -d "$FOLDER/nodes" ]; then
    echo "Error: No nodes/ directory found in $FOLDER"
    exit 1
fi

INDEX_FILE="$FOLDER/nodes/_index.json"

if [ -f "$INDEX_FILE" ]; then
    echo "=== Workflow Nodes ==="
    echo ""
    # Use jq if available, otherwise fall back to grep/sed
    if command -v jq &> /dev/null; then
        jq -r '.[] | "\(.index)\t\(.type | split(".") | .[-1])\t\(.name)"' "$INDEX_FILE" | column -t -s $'\t'
    else
        echo "Index: $INDEX_FILE"
        echo "(Install jq for formatted output)"
        cat "$INDEX_FILE"
    fi
else
    echo "=== Node Files ==="
    ls -1 "$FOLDER/nodes/"*.json 2>/dev/null | while read f; do
        basename "$f"
    done
fi

echo ""
echo "=== Summary ==="
TOTAL=$(ls -1 "$FOLDER/nodes/"*.json 2>/dev/null | grep -v _index | wc -l)
STICKY=$(ls -1 "$FOLDER/nodes/"*stickyNote*.json 2>/dev/null | wc -l)
EXEC=$((TOTAL - STICKY))
echo "Total nodes: $TOTAL"
echo "Execution nodes: $EXEC"
echo "Documentation nodes: $STICKY"
