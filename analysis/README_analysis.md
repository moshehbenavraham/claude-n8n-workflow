# Analysis

Generated workflow analysis reports from the `n8n-workflow-analyzer` skill.

---

## Purpose

Storage for comprehensive markdown analysis documents produced by analyzing n8n workflow folders.

---

## File Naming

```
workflow-analysis-{workflow-name}.md
```

---

## Report Structure

Each analysis report contains:

| Section | Content |
|---------|---------|
| **Metadata** | Workflow ID, name, author, category |
| **Purpose** | Business function and use case |
| **Flow Architecture** | Entry points, execution paths, terminal nodes |
| **Node Inventory** | All nodes with types and configurations |
| **Documentation** | Extracted sticky notes and setup instructions |
| **External Services** | APIs, integrations, credentials required |

---

## Workflow

1. Download workflow via `scripts/download-workflows.sh`
2. Split workflow via `scripts/split-workflows.sh`
3. Analyze via `n8n-workflow-analyzer` skill
4. Report saved here, workflow moved to `archive/`

---

## Related

| Resource | Path |
|----------|------|
| Skill | `.claude/skills/n8n-workflow-analyzer/` |
| Archive | `archive/` |
| Consolidator | `.claude/skills/analysis-consolidator/` |
