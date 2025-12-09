# n8n Workflows

Downloaded n8n workflow JSON files and split workflow folders awaiting analysis.

---

## Purpose

Staging area for workflows downloaded from the n8n template API before analysis.

---

## Contents

| Type | Description |
|------|-------------|
| `*.json` | Raw downloaded workflow files |
| `{name}/` | Split workflow folders (post `split-workflows.sh`) |

---

## Split Folder Structure

```
{workflow-name}/
├── 01-metadata.json      # ID, name, description, author
├── 02-settings.json      # Workflow settings, tags
├── 03-connections.json   # Node connection graph
├── 04-nodes.json         # All nodes (small workflows)
├── 05-template-nodes.json # Template display nodes
└── nodes/                # Individual nodes (large workflows)
    ├── _index.json       # Node manifest
    └── NN-type-Name.json # Per-node files
```

---

## Workflow

| Step | Command |
|------|---------|
| 1. Download | `./scripts/download-workflows.sh <ID>` |
| 2. Split | `./scripts/split-workflows.sh` |
| 3. Analyze | Trigger `n8n-workflow-analyzer` skill |
| 4. Archive | Workflow moves to `archive/` |

---

## Related

| Resource | Path |
|----------|------|
| Download script | `scripts/download-workflows.sh` |
| Split script | `scripts/split-workflows.sh` |
| Search script | `scripts/search-workflows.sh` |
