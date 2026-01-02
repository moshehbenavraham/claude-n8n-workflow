#!/bin/bash
# logging.sh - Structured logging library for shell scripts
#
# Provides:
#   - log_info, log_warn, log_error functions with console output
#   - capture_error for AI-friendly JSON error logs
#   - Automatic last_error_<timestamp>.json creation
#
# Usage:
#   source "$(dirname "${BASH_SOURCE[0]}")/logging.sh"
#   log_info "Processing started"
#   log_error "Failed to download" "download" '{"url":"http://example.com"}'
#   capture_error "ConnectionError" "Failed to connect" "$stack_trace" '{"retry":3}'

# Determine paths
LOGGING_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGGING_PROJECT_ROOT="$(dirname "$LOGGING_SCRIPT_DIR")"
LOGGING_LOGS_DIR="$LOGGING_PROJECT_ROOT/logs"

# Ensure logs directory exists
mkdir -p "$LOGGING_LOGS_DIR"

# Colors for console output
_LOG_RED='\033[0;31m'
_LOG_GREEN='\033[0;32m'
_LOG_YELLOW='\033[1;33m'
_LOG_BLUE='\033[0;34m'
_LOG_NC='\033[0m'

# Get ISO 8601 timestamp
_log_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%S.%3NZ"
}

# Get timestamp for filename (filesystem safe)
_log_file_timestamp() {
    date -u +"%Y-%m-%dT%H-%M-%S"
}

# Log to console with level
log_info() {
    local msg="$1"
    local timestamp
    timestamp=$(_log_timestamp)
    echo -e "${_LOG_BLUE}[$timestamp]${_LOG_NC} ${_LOG_GREEN}INFO${_LOG_NC}  $msg"
}

log_warn() {
    local msg="$1"
    local timestamp
    timestamp=$(_log_timestamp)
    echo -e "${_LOG_BLUE}[$timestamp]${_LOG_NC} ${_LOG_YELLOW}WARN${_LOG_NC}  $msg" >&2
}

log_error() {
    local msg="$1"
    local context="${2:-}"
    local extra_json="${3:-{}}"
    local timestamp
    timestamp=$(_log_timestamp)
    echo -e "${_LOG_BLUE}[$timestamp]${_LOG_NC} ${_LOG_RED}ERROR${_LOG_NC} $msg" >&2

    # Also capture to last_error JSON
    if [[ -n "$context" ]]; then
        capture_error "ShellError" "$msg" "" "$extra_json" "$context"
    fi
}

# Capture structured error to JSON file (AI-friendly format)
# Arguments:
#   $1 - error_type (e.g., "ConnectionError", "ValidationError")
#   $2 - message
#   $3 - stack_trace (optional, can be empty string)
#   $4 - context JSON (optional, default {})
#   $5 - operation name (optional)
capture_error() {
    local error_type="${1:-UnknownError}"
    local message="${2:-No message provided}"
    local stack_trace="${3:-}"
    local context="${4:-}"
    local operation="${5:-}"

    # Validate context is valid JSON, default to empty object
    if [[ -z "$context" ]] || ! echo "$context" | jq -e . >/dev/null 2>&1; then
        context="{}"
    fi

    local timestamp
    local file_timestamp
    timestamp=$(_log_timestamp)
    file_timestamp=$(_log_file_timestamp)

    local output_file="$LOGGING_LOGS_DIR/last_error_${file_timestamp}.json"

    # Build JSON using jq for proper escaping
    local json_output
    json_output=$(jq -n \
        --arg timestamp "$timestamp" \
        --arg level "error" \
        --arg msg "$message" \
        --arg error_type "$error_type" \
        --arg error_message "$message" \
        --arg stack "$stack_trace" \
        --arg operation "$operation" \
        --argjson context "$context" \
        '{
            timestamp: $timestamp,
            level: $level,
            msg: $msg,
            error: {
                type: $error_type,
                message: $error_message,
                stack: (if $stack == "" then null else $stack end)
            },
            context: ($context + (if $operation == "" then {} else {operation: $operation} end))
        }')

    echo "$json_output" > "$output_file"

    # Return the filename for reference
    echo "$output_file"
}

# Trap handler for unexpected errors
# Usage: trap 'handle_script_error $LINENO "$BASH_COMMAND"' ERR
handle_script_error() {
    local line_number="$1"
    local command="$2"
    local script_name="${BASH_SOURCE[1]:-unknown}"

    local stack_trace="at line $line_number in $script_name"

    capture_error \
        "ScriptError" \
        "Command failed: $command" \
        "$stack_trace" \
        "{\"script\": \"$script_name\", \"line\": $line_number}" \
        "script_execution"

    log_error "Script error at line $line_number: $command"
}

# Enable error trapping (call this at the start of your script)
enable_error_capture() {
    set -E
    trap 'handle_script_error $LINENO "$BASH_COMMAND"' ERR
}

# Structured log entry to file (append to daily log)
log_structured() {
    local level="$1"
    local msg="$2"
    local context="${3:-}"

    # Validate context is valid JSON, default to empty object
    if [[ -z "$context" ]] || ! echo "$context" | jq -e . >/dev/null 2>&1; then
        context="{}"
    fi

    local timestamp
    local date_str
    timestamp=$(_log_timestamp)
    date_str=$(date -u +"%Y-%m-%d")

    local log_file="$LOGGING_LOGS_DIR/${date_str}.log"

    local json_entry
    json_entry=$(jq -n -c \
        --arg timestamp "$timestamp" \
        --arg level "$level" \
        --arg msg "$msg" \
        --argjson context "$context" \
        '{timestamp: $timestamp, level: $level, msg: $msg, context: $context}')

    echo "$json_entry" >> "$log_file"
}
