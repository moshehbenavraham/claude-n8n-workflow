#!/bin/bash
# download-workflows.sh
# Downloads n8n workflow JSON files from the n8n template API
#
# Usage:
#   ./scripts/download-workflows.sh <workflow_id>                    # Single ID
#   ./scripts/download-workflows.sh <id1> <id2> <id3>                # Multiple IDs
#   ./scripts/download-workflows.sh "https://n8n.io/workflows/5428-..." # From URL
#   ./scripts/download-workflows.sh --file workflows.txt             # From file (one ID/URL per line)
#   ./scripts/download-workflows.sh --split <id>                     # Download and split
#
# API Reference: https://api.n8n.io/api/templates/workflows/{WORKFLOW_ID}

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_ROOT/n8n-workflows"
API_BASE="https://api.n8n.io/api/templates/workflows"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
RUN_SPLIT=false
VERBOSE=false

# Show usage
usage() {
    cat << EOF
=== n8n Workflow Downloader ===

Usage: $(basename "$0") [OPTIONS] <workflow_id|url> [<workflow_id|url> ...]

Arguments:
  <workflow_id>     Numeric workflow ID (e.g., 5428)
  <url>             Full n8n workflow URL (ID will be extracted)

Options:
  -f, --file FILE   Read workflow IDs/URLs from file (one per line)
  -s, --split       Run split-workflows.sh after downloading
  -o, --output DIR  Output directory (default: n8n-workflows/)
  -v, --verbose     Show verbose output
  -h, --help        Show this help message

Examples:
  $(basename "$0") 5428
  $(basename "$0") 5428 6332 6162
  $(basename "$0") "https://n8n.io/workflows/5428-qualify-leads/"
  $(basename "$0") --file workflow-list.txt --split
  $(basename "$0") -s 5428 6332

EOF
    exit 0
}

# Extract workflow ID from URL or return as-is if already numeric
extract_id() {
    local input="$1"

    # If already numeric, return as-is
    if [[ "$input" =~ ^[0-9]+$ ]]; then
        echo "$input"
        return 0
    fi

    # Extract ID from URL patterns:
    # https://n8n.io/workflows/5428-workflow-name/
    # https://n8n.io/workflows/5428
    if [[ "$input" =~ n8n\.io/workflows/([0-9]+) ]]; then
        echo "${BASH_REMATCH[1]}"
        return 0
    fi

    # Extract from API URL pattern
    # https://api.n8n.io/api/templates/workflows/5428
    if [[ "$input" =~ api\.n8n\.io/api/templates/workflows/([0-9]+) ]]; then
        echo "${BASH_REMATCH[1]}"
        return 0
    fi

    echo ""
    return 1
}

# Download a single workflow
download_workflow() {
    local workflow_id="$1"
    local output_file="$OUTPUT_DIR/workflow-${workflow_id}.json"
    local api_url="${API_BASE}/${workflow_id}"

    if [[ $VERBOSE == true ]]; then
        echo -e "  ${BLUE}API:${NC} $api_url"
    fi

    # Download to temp file first for validation
    local temp_file=$(mktemp)
    local http_code

    http_code=$(curl -s -w "%{http_code}" -o "$temp_file" "$api_url")

    if [[ "$http_code" != "200" ]]; then
        rm -f "$temp_file"
        echo -e "  ${RED}✗ Failed${NC} (HTTP $http_code)"
        return 1
    fi

    # Validate JSON
    if ! jq -e . "$temp_file" > /dev/null 2>&1; then
        rm -f "$temp_file"
        echo -e "  ${RED}✗ Invalid JSON response${NC}"
        return 1
    fi

    # Extract workflow name for better filename
    local workflow_name
    workflow_name=$(jq -r '.workflow.name // empty' "$temp_file" 2>/dev/null || echo "")

    if [[ -n "$workflow_name" ]]; then
        # Sanitize name for filename
        local safe_name
        safe_name=$(echo "$workflow_name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-60)
        output_file="$OUTPUT_DIR/${workflow_id}-${safe_name}.json"
    fi

    # Move temp file to final location
    mv "$temp_file" "$output_file"

    # Get file size
    local file_size
    file_size=$(du -h "$output_file" | cut -f1)

    echo -e "  ${GREEN}✓ Downloaded${NC} -> $(basename "$output_file") ($file_size)"

    if [[ $VERBOSE == true && -n "$workflow_name" ]]; then
        echo -e "    ${BLUE}Name:${NC} $workflow_name"
    fi

    return 0
}

# Parse command line arguments
WORKFLOW_IDS=()
INPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -f|--file)
            INPUT_FILE="$2"
            shift 2
            ;;
        -s|--split)
            RUN_SPLIT=true
            shift
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -*)
            echo -e "${RED}Error: Unknown option $1${NC}"
            usage
            ;;
        *)
            WORKFLOW_IDS+=("$1")
            shift
            ;;
    esac
done

# Read from file if specified
if [[ -n "$INPUT_FILE" ]]; then
    if [[ ! -f "$INPUT_FILE" ]]; then
        echo -e "${RED}Error: File not found: $INPUT_FILE${NC}"
        exit 1
    fi

    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        WORKFLOW_IDS+=("$line")
    done < "$INPUT_FILE"
fi

# Check if we have any workflows to download
if [[ ${#WORKFLOW_IDS[@]} -eq 0 ]]; then
    echo -e "${YELLOW}No workflow IDs provided.${NC}"
    echo ""
    usage
fi

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo -e "${BLUE}n8n Workflow Downloader${NC}"
echo "=============================================="
echo "Output directory: $OUTPUT_DIR"
echo "Workflows to download: ${#WORKFLOW_IDS[@]}"
echo "----------------------------------------------"
echo ""

# Track results
success_count=0
fail_count=0
downloaded_files=()

# Process each workflow
for input in "${WORKFLOW_IDS[@]}"; do
    # Extract ID (|| true prevents set -e from exiting on invalid input)
    workflow_id=$(extract_id "$input" || true)

    if [[ -z "$workflow_id" ]]; then
        echo -e "${YELLOW}⚠ Skipping invalid input:${NC} $input"
        fail_count=$((fail_count + 1))
        continue
    fi

    echo -e "${BLUE}Downloading workflow $workflow_id...${NC}"

    if download_workflow "$workflow_id"; then
        success_count=$((success_count + 1))
        downloaded_files+=("$workflow_id")
    else
        fail_count=$((fail_count + 1))
    fi

    echo ""
done

# Summary
echo "=============================================="
echo -e "${BLUE}Summary${NC}"
echo "----------------------------------------------"
echo -e "  ${GREEN}✓ Success:${NC} $success_count"
echo -e "  ${RED}✗ Failed:${NC}  $fail_count"
echo "=============================================="

# Run split-workflows if requested
if [[ $RUN_SPLIT == true && $success_count -gt 0 ]]; then
    echo ""
    echo "Running split-workflows.sh..."
    echo ""
    "$SCRIPT_DIR/split-workflows.sh"
fi

# Exit with error if any downloads failed
[[ $fail_count -eq 0 ]]
