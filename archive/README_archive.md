# Archive

Processed workflow folders after analysis completion.

---

## Purpose

Storage for analyzed workflow folders. Workflows are moved here automatically after the `n8n-workflow-analyzer` skill generates a report.

---

## Git Status

Contents of this folder (except this README) are excluded via `.gitignore`:
- Keeps repository size manageable
- Original workflows always re-downloadable from n8n API
- Analysis reports preserved in `analysis/`

---

## Contents

| Type | Description |
|------|-------------|
| `{workflow-name}/` | Split workflow folders (post-analysis) |

---

## Workflow Lifecycle

```
n8n-workflows/     →  analysis/          →  archive/
(download/split)      (report generated)    (workflow moved)
```

---

## Recovery

To re-analyze an archived workflow:

```bash
mv archive/{workflow-name} n8n-workflows/
# Then trigger n8n-workflow-analyzer skill
```

---

## Related

| Resource | Path |
|----------|------|
| Analysis reports | `analysis/` |
| Staging area | `n8n-workflows/` |
