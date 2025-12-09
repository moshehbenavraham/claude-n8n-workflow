---
name: n8n-workflow-analyzer
description: This skill should be used when the user asks to "analyze n8n workflow", "understand this workflow", "explain n8n workflow", "review workflow folder", "parse split workflow", "what does this workflow do", mentions a workflow folder path, or wants to understand a chunked/split n8n workflow JSON structure. Provides systematic analysis using sub-agents to build comprehensive workflow understanding.
version: 1.2.0
---

# n8n Workflow Analyzer

## Overview

This skill systematically analyzes split n8n workflow folders to build a comprehensive understanding of workflow purpose, data flow, node functionality, and implementation details. The analysis uses specialized sub-agents to examine different aspects in parallel before assembling a unified understanding.

## Split Workflow Folder Structure

Split workflows follow this structure (created by `split-workflows.sh`):

```
workflow-folder/
├── 01-metadata.json      # Workflow name, description, author, categories
├── 02-settings.json      # Workflow settings, tags, version info
├── 03-connections.json   # Node-to-node connection map (data flow)
├── 05-template-nodes.json # Display/template node info (optional)
└── nodes/
    ├── _index.json       # Node manifest with types and names
    └── NN-type-Name.json # Individual node definitions
```

## Analysis Procedure

### Phase 1: Initial Discovery

Before spawning sub-agents, gather essential context:

1. **Read the node index** at `{folder}/nodes/_index.json` to identify:
   - Total node count
   - Node types present (webhook, httpRequest, code, if, slack, etc.)
   - Execution vs documentation nodes (stickyNote = documentation)

2. **Read metadata** at `{folder}/01-metadata.json` for:
   - Workflow name and description
   - Author information
   - Categories and use case

3. **Read connections** at `{folder}/03-connections.json` for:
   - Data flow between nodes
   - Branching logic (multiple outputs)
   - Entry points (nodes with no incoming connections)

### Phase 2: Parallel Sub-Agent Analysis

Spawn **4 parallel Task agents** using the plugin's custom agents. Call all 4 agents in a single message with multiple Task tool invocations:

#### Agent 1: Metadata Analyzer
Use `subagent_type: "n8n-tools:metadata-analyzer"`:
```
Analyze the n8n workflow metadata and context in {folder}.
Read 01-metadata.json, 02-settings.json, and 05-template-nodes.json (if exists).
Extract workflow purpose, target audience, external services, author info, and categories.
```

#### Agent 2: Flow Analyzer
Use `subagent_type: "n8n-tools:flow-analyzer"`:
```
Analyze the data flow and architecture in {folder}.
Read 03-connections.json and nodes/_index.json.
Map execution paths, branching points, parallel paths, and create an ASCII flow diagram.
```

#### Agent 3: Node Analyzer
Use `subagent_type: "n8n-tools:node-analyzer"`:
```
Analyze all execution nodes in {folder}/nodes/ (skip stickyNote types).
For each node, document type, purpose, parameters, API calls, transformations, and dependencies.
```

#### Agent 4: Docs Extractor
Use `subagent_type: "n8n-tools:docs-extractor"`:
```
Extract all embedded documentation from stickyNote nodes in {folder}/nodes/.
Compile setup instructions, configuration requirements, API key needs, and customization guidance.
```

### Phase 3: Synthesis

After all sub-agents complete, synthesize findings into:

1. **Executive Summary** (2-3 sentences)
2. **Workflow Architecture** (ASCII diagram + explanation)
3. **Implementation Guide**
   - Prerequisites and dependencies
   - Required credentials/API keys
   - Configuration steps
4. **Node Reference Table**
   - Node name, type, purpose, connections
5. **Data Flow Description**
   - What data enters
   - How it transforms
   - What outputs are produced
6. **Customization Points**
   - What can be easily modified
   - What requires deeper changes

### Phase 4: Save Results

After synthesizing the analysis, **always write the results to a markdown file** in the `analysis/` folder:

1. **Derive filename from workflow metadata**:
   - Use the `name` field from `01-metadata.json`
   - Convert to kebab-case (lowercase, spaces/special chars to hyphens)
   - Prefix with `workflow-analysis-`
   - Example: "Automated Real Estate Property Lead Scoring with BatchData" → `workflow-analysis-automated-real-estate-property-lead-scoring-with-batchdata.md`

2. **Ensure analysis directory exists and write file**:
   - First create the directory: `mkdir -p {project_root}/analysis`
   - Use the Write tool to save the complete analysis
   - Target path: `{project_root}/analysis/workflow-analysis-{workflow-name-kebab}.md`

3. **Confirm to user**:
   - After writing, inform the user of the file location
   - Example: "Analysis saved to `/path/to/project/analysis/workflow-analysis-example-workflow.md`"

### Phase 5: Archive Workflow (MANDATORY)

After saving the analysis, **automatically archive the analyzed workflow**. This step is **non-optional** and must always execute.

#### Archive Process

1. **Determine paths**:
   ```
   WORKFLOW_FOLDER = the folder you analyzed (e.g., /home/.../n8n-workflows/3664-property-lead-scoring-batchdata)
   WORKFLOW_JSON   = same path + ".json" (e.g., /home/.../n8n-workflows/3664-property-lead-scoring-batchdata.json)
   PROJECT_ROOT    = /home/aiwithapex/projects/real-estate
   ARCHIVE_DIR     = {PROJECT_ROOT}/archive
   ```

2. **Ensure archive directory exists**:
   ```bash
   mkdir -p /home/aiwithapex/projects/real-estate/archive
   ```

3. **Move the split workflow folder**:
   ```bash
   mv "{WORKFLOW_FOLDER}" /home/aiwithapex/projects/real-estate/archive/
   ```

4. **Move the original JSON file** (if it exists):
   ```bash
   mv "{WORKFLOW_JSON}" /home/aiwithapex/projects/real-estate/archive/
   ```
   - Note: The JSON file is always in the same directory as the folder, with the same base name + `.json`

5. **Verify and confirm**:
   - Run `ls /home/aiwithapex/projects/real-estate/archive/` to confirm both items moved
   - Report to user: "✓ Archived: `{folder_name}/` and `{folder_name}.json` → `archive/`"

#### Example Commands

For a workflow at `n8n-workflows/6310-zillow-listings-telegram-scrapegraphai`:

```bash
# Create archive dir (idempotent)
mkdir -p /home/aiwithapex/projects/real-estate/archive

# Move folder and JSON
mv /home/aiwithapex/projects/real-estate/n8n-workflows/6310-zillow-listings-telegram-scrapegraphai /home/aiwithapex/projects/real-estate/archive/
mv /home/aiwithapex/projects/real-estate/n8n-workflows/6310-zillow-listings-telegram-scrapegraphai.json /home/aiwithapex/projects/real-estate/archive/

# Verify
ls -la /home/aiwithapex/projects/real-estate/archive/ | grep 6310
```

#### Critical Rules

- **ALWAYS execute** - Never skip archival, never ask for confirmation
- **Execute IMMEDIATELY** after writing the analysis markdown
- **Handle missing JSON gracefully** - If `.json` file doesn't exist, proceed without error
- **Report success** - Always confirm to user what was archived

## Node Type Reference

Common n8n node types encountered:

| Type | Purpose |
|------|---------|
| `webhook` | Entry point - receives external HTTP requests |
| `httpRequest` | Makes outbound API calls |
| `code` | Custom JavaScript/Python logic |
| `if` | Conditional branching |
| `switch` | Multi-way branching |
| `set` | Set/transform field values |
| `merge` | Combine data from multiple paths |
| `splitInBatches` | Process items in chunks |
| `function` | Legacy code node |
| `stickyNote` | Documentation (not executed) |
| `slack`/`discord`/etc. | Integration-specific nodes |

## Output Format

Present analysis in this structure:

```markdown
# Workflow Analysis: {Workflow Name}

## Quick Summary
{2-3 sentence overview}

## Workflow Diagram
{ASCII representation of flow}

## Purpose & Use Cases
{Expanded description from metadata}

## Technical Architecture

### Entry Points
{Triggers and how workflow is activated}

### Processing Pipeline
{Step-by-step data flow}

### Outputs & Actions
{What the workflow produces/does}

## Implementation Requirements

### External Services
{APIs, services needed}

### Credentials Required
{Authentication needs}

### Configuration Steps
{Setup instructions compiled from stickyNotes}

## Node Details
{Table of all execution nodes}

## Customization Guide
{How to adapt for different use cases}
```

## Tips for Effective Analysis

1. **Start with _index.json** - Quick overview without reading all nodes
2. **Prioritize code nodes** - Often contain core business logic
3. **Follow the connections** - Trace data flow from trigger to outputs
4. **Read stickyNotes** - Authors often embed critical setup info
5. **Identify patterns** - Many workflows follow common patterns (API enrichment, conditional routing, notification chains)

## Additional Resources

### Reference Files

- **`references/node-types.md`** - Comprehensive n8n node type documentation
- **`references/analysis-patterns.md`** - Common workflow patterns and how to identify them

### Scripts

- **`scripts/list-nodes.sh`** - Quick node listing utility
