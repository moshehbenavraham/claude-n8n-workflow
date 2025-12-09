# Skills

Claude Code custom skills for n8n workflow analysis.

---

## Purpose

Skills extend Claude's capabilities with specialized knowledge and workflows. Each skill is invoked automatically based on trigger phrases or via explicit commands.

---

## Available Skills

| Skill | Version | Purpose |
|-------|---------|---------|
| `n8n-workflow-analyzer` | 1.2.0 | Systematic workflow analysis using parallel sub-agents |
| `analysis-consolidator` | 1.3.0 | Consolidate analyses into unified architecture |

---

## Skill Structure

```
{skill-name}/
├── SKILL.md          # Main skill definition (required)
├── references/       # Supporting documentation (optional)
└── scripts/          # Helper scripts (optional)
```

---

## Invocation

| Method | Example |
|--------|---------|
| Trigger phrase | "analyze n8n workflow" |
| Direct request | "use the n8n-workflow-analyzer skill" |

---

## Related

| Resource | Path |
|----------|------|
| Agents | `.claude/agents/` |
| Claude config | `.claude/README_p_claude.md` |
