# Agents

Claude Code custom sub-agents for workflow analysis tasks.

---

## Purpose

Sub-agents are specialized Task tool configurations with defined tools, models, and prompts. They handle focused analysis tasks and can run in parallel.

---

## Available Agents

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| `analysis-extractor` | sonnet | Read, Glob, Grep | Extract patterns from analysis docs |
| `docs-extractor` | haiku | Read, Glob, Grep | Extract sticky note documentation |
| `flow-analyzer` | haiku | Read, Glob, Grep | Map data flow architecture |
| `metadata-analyzer` | haiku | Read, Glob, Grep | Extract workflow context |
| `node-analyzer` | sonnet | Read, Glob, Grep | Deep node configuration analysis |
| `pattern-aggregator` | sonnet | Read | Combine extraction reports |
| `solution-architect` | sonnet | Read, Write, Bash | Generate architecture docs |

---

## Invocation

```javascript
// Via Task tool
{
  "subagent_type": "flow-analyzer",
  "prompt": "Analyze data flow in workflow-folder/"
}
```

---

## Agent File Format

Each `.md` file contains YAML frontmatter:

```yaml
---
name: agent-name
model: haiku|sonnet
description: When to use this agent
tools: [Read, Glob, Grep]
---
```

Followed by the system prompt defining agent behavior.

---

## Related

| Resource | Path |
|----------|------|
| Skills | `.claude/skills/` |
| Claude config | `.claude/README_p_claude.md` |
