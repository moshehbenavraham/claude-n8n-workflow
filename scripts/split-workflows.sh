#!/bin/bash
# split-workflows.sh
# Splits n8n workflow JSON files into organized, manageable chunks
#
# Usage: ./scripts/split-workflows.sh [line_threshold]
#   line_threshold: Max lines before splitting (default: 300)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORKFLOW_DIR="$PROJECT_ROOT/n8n-workflows"
LINE_THRESHOLD="${1:-300}"

cd "$WORKFLOW_DIR"

echo "=== n8n Workflow Splitter ==="
echo "Working directory: $WORKFLOW_DIR"
echo "Line threshold: $LINE_THRESHOLD"
echo ""

# Track success/failure counts
success_count=0
failure_count=0

# Process each JSON file
for json_file in *.json; do
    [ -f "$json_file" ] || continue

    # Extract base name (remove .json)
    base_name="${json_file%.json}"

    echo "Processing: $json_file"

    # Create folder for this workflow
    mkdir -p "$base_name"

    # Use Python for intelligent JSON splitting
    # Pass variables via environment to avoid shell escaping issues
    if WORKFLOW_JSON_FILE="$json_file" WORKFLOW_OUTPUT_DIR="$base_name" WORKFLOW_LINE_THRESHOLD="$LINE_THRESHOLD" python3 << 'PYTHON_EOF'
import json
import os
import sys

# Get parameters from environment variables (safe from shell escaping issues)
json_file = os.environ.get('WORKFLOW_JSON_FILE')
output_dir = os.environ.get('WORKFLOW_OUTPUT_DIR')
line_threshold = int(os.environ.get('WORKFLOW_LINE_THRESHOLD', 300))

if not json_file or not output_dir:
    print("  ERROR: Missing required environment variables", file=sys.stderr)
    sys.exit(1)

def write_json(filepath, data, indent=2):
    """Write JSON with consistent formatting"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)
    # Return line count
    with open(filepath, 'r') as f:
        return len(f.readlines())

def count_formatted_lines(data):
    """Count lines when JSON is formatted"""
    return len(json.dumps(data, indent=2).split('\n'))

def sanitize_filename(name):
    """Sanitize a string for use in a filename"""
    # Replace problematic characters
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\r', '\t']:
        name = name.replace(char, '_')
    return name

try:
    # Load the workflow
    with open(json_file, 'r') as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    print(f"  ERROR: Invalid JSON - {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"  ERROR: Failed to read file - {e}", file=sys.stderr)
    sys.exit(1)

try:
    total_lines = count_formatted_lines(data)
    print(f"  Total formatted lines: {total_lines}")

    # Check if small enough to keep intact
    if total_lines <= line_threshold:
        print(f"  -> Workflow is compact ({total_lines} lines), keeping intact")
        write_json(os.path.join(output_dir, 'workflow.json'), data)
        print(f"  -> Created: {output_dir}/workflow.json")
    else:
        print(f"  -> Workflow exceeds threshold, splitting intelligently...")

        # Extract the main workflow object
        workflow = data.get('workflow', data)
        inner_workflow = workflow.get('workflow', {})

        # 1. Extract metadata (everything except heavy data)
        metadata = {
            'id': workflow.get('id'),
            'name': workflow.get('name'),
            'description': workflow.get('description'),
            'createdAt': workflow.get('createdAt'),
            'views': workflow.get('views'),
            'totalViews': workflow.get('totalViews'),
            'status': workflow.get('status'),
            'user': workflow.get('user'),
            'categories': workflow.get('categories'),
            'workflowInfo': workflow.get('workflowInfo'),
            'lastUpdatedBy': workflow.get('lastUpdatedBy'),
        }
        # Remove None values
        metadata = {k: v for k, v in metadata.items() if v is not None}
        write_json(os.path.join(output_dir, '01-metadata.json'), metadata)
        print(f"  -> Created: {output_dir}/01-metadata.json")

        # 2. Extract workflow settings/meta
        if inner_workflow:
            settings = {
                'id': inner_workflow.get('id'),
                'name': inner_workflow.get('name'),
                'meta': inner_workflow.get('meta'),
                'tags': inner_workflow.get('tags'),
                'active': inner_workflow.get('active'),
                'pinData': inner_workflow.get('pinData'),
                'settings': inner_workflow.get('settings'),
                'versionId': inner_workflow.get('versionId'),
            }
            settings = {k: v for k, v in settings.items() if v is not None}
            write_json(os.path.join(output_dir, '02-settings.json'), settings)
            print(f"  -> Created: {output_dir}/02-settings.json")

        # 3. Extract connections
        connections = inner_workflow.get('connections', {})
        if connections:
            write_json(os.path.join(output_dir, '03-connections.json'), connections)
            print(f"  -> Created: {output_dir}/03-connections.json")

        # 4. Extract nodes - split if too many
        nodes = inner_workflow.get('nodes', [])
        if nodes:
            nodes_lines = count_formatted_lines(nodes)

            if nodes_lines <= line_threshold:
                # Keep all nodes in one file
                write_json(os.path.join(output_dir, '04-nodes.json'), nodes)
                print(f"  -> Created: {output_dir}/04-nodes.json ({len(nodes)} nodes)")
            else:
                # Split nodes into individual files
                nodes_dir = os.path.join(output_dir, 'nodes')
                os.makedirs(nodes_dir, exist_ok=True)

                # Create index file
                node_index = []
                for i, node in enumerate(nodes):
                    node_name = sanitize_filename(node.get('name', f'node_{i}'))
                    node_type = node.get('type', 'unknown').split('.')[-1]
                    filename = f"{i:02d}-{node_type}-{node_name[:30]}.json"

                    write_json(os.path.join(nodes_dir, filename), node)
                    node_index.append({
                        'index': i,
                        'file': filename,
                        'name': node.get('name'),
                        'type': node.get('type')
                    })

                write_json(os.path.join(nodes_dir, '_index.json'), node_index)
                print(f"  -> Created: {output_dir}/nodes/ ({len(nodes)} node files)")

        # 5. Extract outer nodes (template display info) if present
        outer_nodes = workflow.get('nodes', [])
        if outer_nodes and outer_nodes != nodes:
            write_json(os.path.join(output_dir, '05-template-nodes.json'), outer_nodes)
            print(f"  -> Created: {output_dir}/05-template-nodes.json")

        # 6. Save image URL separately if present
        if workflow.get('image'):
            image_data = {'image': workflow.get('image')}
            write_json(os.path.join(output_dir, '06-image.json'), image_data)
            print(f"  -> Created: {output_dir}/06-image.json")

    print(f"  Done!")

except Exception as e:
    print(f"  ERROR: Failed to process workflow - {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF
    then
        success_count=$((success_count + 1))
    else
        failure_count=$((failure_count + 1))
        echo "  WARNING: Failed to process $json_file (continuing...)"
    fi

    echo ""
done

echo "=== Summary ==="
echo "Successful: $success_count"
echo "Failed: $failure_count"
echo ""
echo "Processed workflows:"
for dir in */; do
    [ -d "$dir" ] || continue
    file_count=$(find "$dir" -name "*.json" | wc -l)
    echo "  $dir -> $file_count file(s)"
done

# Exit with error if any failures occurred
if [ "$failure_count" -gt 0 ]; then
    exit 1
fi
