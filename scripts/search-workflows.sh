#!/bin/bash
# search-workflows.sh
# Search n8n workflow templates using the public API
#
# Usage:
#   ./scripts/search-workflows.sh "real estate"              # Basic search
#   ./scripts/search-workflows.sh --category AI              # Filter by category
#   ./scripts/search-workflows.sh --apps Telegram,OpenAI     # Filter by apps
#   ./scripts/search-workflows.sh --list-categories          # List all categories
#   ./scripts/search-workflows.sh --list-collections         # List all collections
#   ./scripts/search-workflows.sh --ids "real estate"        # Output only IDs (for piping)
#
# API Reference: docs/n8n-public-API.md

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# API Configuration
API_BASE="https://api.n8n.io/api/templates"
API_HEALTH="https://api.n8n.io/api/health"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

# Default values
ROWS=10
SKIP=0
OUTPUT_FORMAT="table"  # table, json, ids, compact
SHOW_FILTERS=false
N_APPS=10
N_CATEGORIES=10

# Search parameters
SEARCH_QUERY=""
CATEGORY_FILTER=""
APPS_FILTER=""
NODES_FILTER=""

# Command modes
LIST_CATEGORIES=false
LIST_COLLECTIONS=false
GET_COLLECTION=""
CHECK_HEALTH=false
SHOW_STATS=false
SAVE_RESULTS=false
SAVE_DIR="search_results"

# Show usage
usage() {
    cat << 'EOF'
=== n8n Workflow Search Tool ===

Search and explore n8n workflow templates using the public API.

USAGE:
  search-workflows.sh [OPTIONS] [SEARCH_QUERY]

SEARCH OPTIONS:
  -q, --query QUERY       Search query string
  -c, --category CAT      Filter by category (comma-separated for multiple)
  -a, --apps APPS         Filter by app/integration names (comma-separated)
  -n, --nodes NODES       Filter by node type names (comma-separated)
  -r, --rows NUM          Number of results to return (default: 10, max: 100)
  -p, --page NUM          Page number (calculates skip automatically)
  -s, --skip NUM          Skip N results (for manual pagination)
  --show-filters          Show available filter counts in search results

OUTPUT OPTIONS:
  -o, --output FORMAT     Output format: table, json, ids, compact (default: table)
  --json                  Shorthand for --output json
  --ids                   Shorthand for --output ids (for piping to download script)
  --compact               Shorthand for --output compact
  --save                  Save results to search_results/ folder (JSON format)

DISCOVERY OPTIONS:
  --list-categories       List all available categories
  --list-collections      List all curated collections
  --collection ID         Get details for a specific collection
  --stats                 Show API statistics (total workflows, etc.)
  --health                Check API health status

GENERAL:
  -v, --verbose           Show verbose output including API URLs
  -h, --help              Show this help message

EXAMPLES:
  # Basic keyword search
  search-workflows.sh "real estate"
  search-workflows.sh -q "telegram bot"

  # Filter by category
  search-workflows.sh --category AI
  search-workflows.sh --category "AI,Marketing"

  # Filter by apps/integrations
  search-workflows.sh --apps "Telegram,OpenAI"
  search-workflows.sh -a Gmail -q "lead"

  # Filter by specific node types
  search-workflows.sh --nodes "n8n-nodes-base.telegram"

  # Combine filters
  search-workflows.sh -q "chatbot" -c AI -a Telegram --rows 20

  # Pagination
  search-workflows.sh -q "automation" --rows 20 --page 2
  search-workflows.sh -q "automation" -r 50 -s 100

  # Output formats
  search-workflows.sh -q "real estate" --json
  search-workflows.sh -q "real estate" --ids | xargs ./scripts/download-workflows.sh
  search-workflows.sh --category AI --compact -r 50

  # Save results to file
  search-workflows.sh -q "real estate" --save
  search-workflows.sh --category AI --save -r 50

  # Discovery
  search-workflows.sh --list-categories
  search-workflows.sh --list-collections
  search-workflows.sh --collection 8
  search-workflows.sh --stats

EOF
    exit 0
}

# Check if jq is available
check_dependencies() {
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}Error: jq is required but not installed.${NC}"
        echo "Install with: sudo apt install jq"
        exit 1
    fi
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}Error: curl is required but not installed.${NC}"
        exit 1
    fi
}

# URL encode a string
urlencode() {
    local string="$1"
    python3 -c "import urllib.parse; print(urllib.parse.quote('$string', safe=''))" 2>/dev/null || \
    echo "$string" | sed 's/ /+/g'
}

# Make API request with error handling
api_request() {
    local endpoint="$1"
    local url="${API_BASE}${endpoint}"

    if [[ $VERBOSE == true ]]; then
        echo -e "${DIM}API: $url${NC}" >&2
    fi

    local response
    local http_code
    local temp_file=$(mktemp)

    http_code=$(curl -s -w "%{http_code}" -o "$temp_file" "$url")

    if [[ "$http_code" != "200" ]]; then
        echo -e "${RED}Error: API request failed (HTTP $http_code)${NC}" >&2
        rm -f "$temp_file"
        return 1
    fi

    # Check for API error in response body
    if jq -e '.error' "$temp_file" > /dev/null 2>&1; then
        local error_msg=$(jq -r '.error.message // "Unknown error"' "$temp_file")
        echo -e "${RED}Error: $error_msg${NC}" >&2
        rm -f "$temp_file"
        return 1
    fi

    cat "$temp_file"
    rm -f "$temp_file"
}

# Check API health
check_api_health() {
    echo -e "${BLUE}Checking API health...${NC}"

    local response
    response=$(curl -s "$API_HEALTH")

    if [[ $(echo "$response" | jq -r '.status // empty') == "OK" ]]; then
        echo -e "${GREEN}✓ API is healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ API health check failed${NC}"
        echo "$response"
        return 1
    fi
}

# Show API statistics
show_stats() {
    echo -e "${BLUE}Fetching API statistics...${NC}"
    echo ""

    local response
    response=$(api_request "/workflows?rows=1&skip=0")

    if [[ $? -ne 0 ]]; then
        return 1
    fi

    local total_workflows=$(echo "$response" | jq -r '.totalWorkflows')

    # Get category stats
    local cat_response
    cat_response=$(api_request "/categories")
    local total_categories=$(echo "$cat_response" | jq '.categories | length')

    # Get collection stats
    local col_response
    col_response=$(api_request "/collections")
    local total_collections=$(echo "$col_response" | jq '.collections | length')

    echo -e "${BOLD}=== n8n Template API Statistics ===${NC}"
    echo ""
    echo -e "  ${CYAN}Total Workflows:${NC}    $total_workflows"
    echo -e "  ${CYAN}Total Categories:${NC}   $total_categories"
    echo -e "  ${CYAN}Total Collections:${NC}  $total_collections"
    echo ""
    echo -e "${DIM}Data cached for 4 hours by Cloudflare${NC}"
}

# List all categories
list_categories() {
    local response
    response=$(api_request "/categories")

    if [[ $? -ne 0 ]]; then
        return 1
    fi

    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        echo "$response" | jq '.'
        return 0
    fi

    echo -e "${BOLD}=== n8n Workflow Categories ===${NC}"
    echo ""

    # Group by parent category
    echo -e "${CYAN}Parent Categories:${NC}"
    echo "$response" | jq -r '.categories[] | select(.parent == null) | "  \(.icon) \(.name)"'

    echo ""
    echo -e "${CYAN}Subcategories:${NC}"
    echo "$response" | jq -r '
        .categories[]
        | select(.parent != null)
        | "  \(.icon) \(.name) (parent: \(.parent.name))"
    '

    echo ""
    local count=$(echo "$response" | jq '.categories | length')
    echo -e "${DIM}Total: $count categories${NC}"
}

# List all collections
list_collections() {
    local response
    response=$(api_request "/collections")

    if [[ $? -ne 0 ]]; then
        return 1
    fi

    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        echo "$response" | jq '.'
        return 0
    fi

    echo -e "${BOLD}=== n8n Curated Collections ===${NC}"
    echo ""

    printf "${CYAN}%-4s  %-40s  %s${NC}\n" "ID" "Name" "Workflows"
    echo "--------------------------------------------------------------"

    echo "$response" | jq -r '.collections | sort_by(.rank) | .[] | "\(.id)|\(.name)|\(.workflows | length)"' | \
    while IFS='|' read -r id name workflow_count; do
        printf "%-4s  %-40s  %s\n" "$id" "$name" "$workflow_count"
    done

    echo ""
    local count=$(echo "$response" | jq '.collections | length')
    echo -e "${DIM}Total: $count collections${NC}"
}

# Get specific collection details
get_collection() {
    local collection_id="$1"
    local response
    response=$(api_request "/collections/${collection_id}")

    if [[ $? -ne 0 ]]; then
        return 1
    fi

    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        echo "$response" | jq '.'
        return 0
    fi

    if [[ "$OUTPUT_FORMAT" == "ids" ]]; then
        echo "$response" | jq -r '.collection.workflows[].id'
        return 0
    fi

    local name=$(echo "$response" | jq -r '.collection.name')
    local description=$(echo "$response" | jq -r '.collection.description // "No description"')
    local workflow_count=$(echo "$response" | jq '.collection.workflows | length')

    echo -e "${BOLD}=== Collection: $name ===${NC}"
    echo ""
    echo -e "${CYAN}Description:${NC}"
    echo "$description" | fold -s -w 80 | sed 's/^/  /'
    echo ""
    echo -e "${CYAN}Workflows ($workflow_count):${NC}"
    echo ""

    printf "  ${DIM}%-8s  %-50s  %s${NC}\n" "ID" "Name" "Views"
    echo "  ------------------------------------------------------------------------"

    echo "$response" | jq -r '.collection.workflows[] | "\(.id)|\(.name)|\(.totalViews // .views // 0)"' | \
    while IFS='|' read -r id name views; do
        # Truncate name if too long
        if [[ ${#name} -gt 48 ]]; then
            name="${name:0:45}..."
        fi
        printf "  %-8s  %-50s  %s\n" "$id" "$name" "$views"
    done
}

# Format number with commas
format_number() {
    printf "%'d" "$1" 2>/dev/null || echo "$1"
}

# Search workflows
search_workflows() {
    # Build query string
    local query_params=""
    local separator="?"

    if [[ -n "$SEARCH_QUERY" ]]; then
        local encoded_query=$(urlencode "$SEARCH_QUERY")
        query_params="${query_params}${separator}search=${encoded_query}"
        separator="&"
    fi

    if [[ -n "$CATEGORY_FILTER" ]]; then
        local encoded_category=$(urlencode "$CATEGORY_FILTER")
        query_params="${query_params}${separator}category=${encoded_category}"
        separator="&"
    fi

    if [[ -n "$APPS_FILTER" ]]; then
        local encoded_apps=$(urlencode "$APPS_FILTER")
        query_params="${query_params}${separator}apps=${encoded_apps}"
        separator="&"
    fi

    if [[ -n "$NODES_FILTER" ]]; then
        local encoded_nodes=$(urlencode "$NODES_FILTER")
        query_params="${query_params}${separator}nodes=${encoded_nodes}"
        separator="&"
    fi

    query_params="${query_params}${separator}rows=${ROWS}&skip=${SKIP}"

    if [[ $SHOW_FILTERS == true ]]; then
        query_params="${query_params}&nApps=${N_APPS}&nCategories=${N_CATEGORIES}"
    fi

    local response
    response=$(api_request "/search${query_params}")

    if [[ $? -ne 0 ]]; then
        return 1
    fi

    # Save results if requested
    if [[ $SAVE_RESULTS == true ]]; then
        save_results "$response"
    fi

    # Output based on format
    case "$OUTPUT_FORMAT" in
        json)
            echo "$response" | jq '.'
            ;;
        ids)
            echo "$response" | jq -r '.workflows[].id'
            ;;
        compact)
            output_compact "$response"
            ;;
        table|*)
            output_table "$response"
            ;;
    esac
}

# Output in compact format
output_compact() {
    local response="$1"
    local total=$(echo "$response" | jq -r '.totalWorkflows')
    local count=$(echo "$response" | jq '.workflows | length')

    echo -e "${DIM}Found $total workflows (showing $count)${NC}"
    echo ""

    echo "$response" | jq -r '.workflows[] | "\(.id) | \(.name) | \(.totalViews) views"'
}

# Output in table format
output_table() {
    local response="$1"
    local total=$(echo "$response" | jq -r '.totalWorkflows')
    local count=$(echo "$response" | jq '.workflows | length')
    local current_page=$((SKIP / ROWS + 1))
    local total_pages=$(( (total + ROWS - 1) / ROWS ))

    # Header
    echo -e "${BOLD}=== n8n Workflow Search Results ===${NC}"
    echo ""

    # Search info
    if [[ -n "$SEARCH_QUERY" ]]; then
        echo -e "${CYAN}Search:${NC}   \"$SEARCH_QUERY\""
    fi
    if [[ -n "$CATEGORY_FILTER" ]]; then
        echo -e "${CYAN}Category:${NC} $CATEGORY_FILTER"
    fi
    if [[ -n "$APPS_FILTER" ]]; then
        echo -e "${CYAN}Apps:${NC}     $APPS_FILTER"
    fi
    if [[ -n "$NODES_FILTER" ]]; then
        echo -e "${CYAN}Nodes:${NC}    $NODES_FILTER"
    fi

    echo -e "${CYAN}Results:${NC}  $(format_number $total) total (page $current_page of $total_pages)"
    echo ""

    if [[ $count -eq 0 ]]; then
        echo -e "${YELLOW}No workflows found matching your criteria.${NC}"
        return 0
    fi

    # Table header
    printf "${DIM}%-8s  %-55s  %-10s  %s${NC}\n" "ID" "Name" "Views" "Author"
    echo "------------------------------------------------------------------------------------------------"

    # Table rows
    echo "$response" | jq -r '.workflows[] | "\(.id)|\(.name)|\(.totalViews)|\(.user.name // "Unknown")"' | \
    while IFS='|' read -r id name views author; do
        # Truncate name if too long
        if [[ ${#name} -gt 53 ]]; then
            name="${name:0:50}..."
        fi
        # Truncate author if too long
        if [[ ${#author} -gt 15 ]]; then
            author="${author:0:12}..."
        fi
        printf "%-8s  %-55s  %-10s  %s\n" "$id" "$name" "$(format_number $views)" "$author"
    done

    echo ""

    # Show filters if requested
    if [[ $SHOW_FILTERS == true ]]; then
        echo -e "${CYAN}Available Filters:${NC}"
        echo ""

        # Categories
        echo -e "  ${MAGENTA}Categories:${NC}"
        echo "$response" | jq -r '.filters[] | select(.field_name == "categories") | .counts[:5][] | "    \(.value): \(.count)"' 2>/dev/null || true

        echo ""

        # Apps
        echo -e "  ${MAGENTA}Apps:${NC}"
        echo "$response" | jq -r '.filters[] | select(.field_name == "apps") | .counts[:5][] | "    \(.value): \(.count)"' 2>/dev/null || true

        echo ""
    fi

    # Pagination hint
    if [[ $total -gt $((SKIP + ROWS)) ]]; then
        local next_page=$((current_page + 1))
        echo -e "${DIM}More results available. Use --page $next_page to see next page.${NC}"
    fi
}

# Save results to file
save_results() {
    local response="$1"
    local timestamp=$(date +%Y%m%d-%H%M%S)

    # Build filename from search parameters
    local filename_parts=()

    if [[ -n "$SEARCH_QUERY" ]]; then
        # Sanitize query for filename
        local safe_query=$(echo "$SEARCH_QUERY" | tr ' ' '-' | tr -cd '[:alnum:]-_' | cut -c1-30)
        filename_parts+=("q-${safe_query}")
    fi

    if [[ -n "$CATEGORY_FILTER" ]]; then
        local safe_cat=$(echo "$CATEGORY_FILTER" | tr ',' '-' | tr -cd '[:alnum:]-_' | cut -c1-20)
        filename_parts+=("cat-${safe_cat}")
    fi

    if [[ -n "$APPS_FILTER" ]]; then
        local safe_apps=$(echo "$APPS_FILTER" | tr ',' '-' | tr -cd '[:alnum:]-_' | cut -c1-20)
        filename_parts+=("apps-${safe_apps}")
    fi

    if [[ -n "$NODES_FILTER" ]]; then
        local safe_nodes=$(echo "$NODES_FILTER" | tr ',' '-' | tr -cd '[:alnum:]-_' | cut -c1-20)
        filename_parts+=("nodes-${safe_nodes}")
    fi

    # Default name if no filters
    if [[ ${#filename_parts[@]} -eq 0 ]]; then
        filename_parts+=("search")
    fi

    local filename="${timestamp}_$(IFS='_'; echo "${filename_parts[*]}").json"
    local filepath="${PROJECT_ROOT}/${SAVE_DIR}/${filename}"

    # Create directory if needed
    mkdir -p "${PROJECT_ROOT}/${SAVE_DIR}"

    # Save formatted JSON
    echo "$response" | jq '.' > "$filepath"

    echo -e "${GREEN}✓ Results saved to:${NC} ${SAVE_DIR}/${filename}"
}

# Parse command line arguments
VERBOSE=false
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -q|--query)
            SEARCH_QUERY="$2"
            shift 2
            ;;
        -c|--category)
            CATEGORY_FILTER="$2"
            shift 2
            ;;
        -a|--apps)
            APPS_FILTER="$2"
            shift 2
            ;;
        -n|--nodes)
            NODES_FILTER="$2"
            shift 2
            ;;
        -r|--rows)
            ROWS="$2"
            if [[ $ROWS -gt 100 ]]; then
                echo -e "${YELLOW}Warning: Maximum rows is 100. Setting to 100.${NC}" >&2
                ROWS=100
            fi
            shift 2
            ;;
        -p|--page)
            local page="$2"
            SKIP=$(( (page - 1) * ROWS ))
            shift 2
            ;;
        -s|--skip)
            SKIP="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --json)
            OUTPUT_FORMAT="json"
            shift
            ;;
        --ids)
            OUTPUT_FORMAT="ids"
            shift
            ;;
        --compact)
            OUTPUT_FORMAT="compact"
            shift
            ;;
        --show-filters)
            SHOW_FILTERS=true
            shift
            ;;
        --list-categories)
            LIST_CATEGORIES=true
            shift
            ;;
        --list-collections)
            LIST_COLLECTIONS=true
            shift
            ;;
        --collection)
            GET_COLLECTION="$2"
            shift 2
            ;;
        --stats)
            SHOW_STATS=true
            shift
            ;;
        --health)
            CHECK_HEALTH=true
            shift
            ;;
        --save)
            SAVE_RESULTS=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -*)
            echo -e "${RED}Error: Unknown option $1${NC}" >&2
            echo "Use --help for usage information." >&2
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

# Handle positional args as search query
if [[ ${#POSITIONAL_ARGS[@]} -gt 0 && -z "$SEARCH_QUERY" ]]; then
    SEARCH_QUERY="${POSITIONAL_ARGS[*]}"
fi

# Check dependencies
check_dependencies

# Execute the requested operation
if [[ $CHECK_HEALTH == true ]]; then
    check_api_health
    exit $?
fi

if [[ $SHOW_STATS == true ]]; then
    show_stats
    exit $?
fi

if [[ $LIST_CATEGORIES == true ]]; then
    list_categories
    exit $?
fi

if [[ $LIST_COLLECTIONS == true ]]; then
    list_collections
    exit $?
fi

if [[ -n "$GET_COLLECTION" ]]; then
    get_collection "$GET_COLLECTION"
    exit $?
fi

# Default: run search
# If no search criteria provided, show usage hint
if [[ -z "$SEARCH_QUERY" && -z "$CATEGORY_FILTER" && -z "$APPS_FILTER" && -z "$NODES_FILTER" ]]; then
    echo -e "${YELLOW}No search criteria provided.${NC}"
    echo ""
    echo "Quick examples:"
    echo "  $0 \"real estate\"           # Search by keyword"
    echo "  $0 --category AI            # Filter by category"
    echo "  $0 --list-categories        # See available categories"
    echo "  $0 --help                   # Full usage"
    echo ""
    exit 1
fi

search_workflows
