# References

Supporting documentation for the n8n-workflow-analyzer skill.

---

## Purpose

Reference materials that agents can consult during workflow analysis.

---

## Contents

| File | Description |
|------|-------------|
| `node-types.md` | Comprehensive n8n node type documentation |
| `analysis-patterns.md` | Common workflow architecture patterns |

---

## node-types.md

Node categories and their purposes:

| Category | Examples |
|----------|----------|
| Triggers | webhook, schedule, manualTrigger |
| Processing | httpRequest, code, set, function |
| Conditionals | if, switch, filter |
| Combination | merge, splitInBatches |
| Utility | noOp, stickyNote, wait |
| Integrations | slack, discord, gmail, airtable |
| Error Handling | errorTrigger, stopAndError |

---

## analysis-patterns.md

Common workflow patterns:

| Pattern | Description |
|---------|-------------|
| API Enrichment | Fetch → Process → Store |
| Conditional Routing | Process → IF/Switch → Actions |
| Fan-Out/Fan-In | Split → Parallel → Merge |
| Webhook Response | Receive → Process → Respond |
| Scheduled Batch | Schedule → Loop → Report |

---

## Related

| Resource | Path |
|----------|------|
| Skill definition | `../SKILL.md` |
| Helper scripts | `../scripts/` |
