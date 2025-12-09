# Search Results

Saved search results from `scripts/search-workflows.sh --save`.

---

## Purpose

Storage for n8n template search results in JSON format for later review, filtering, or batch downloading.

---

## File Naming

```
{YYYYMMDD}-{HHMMSS}_q-{query}.json
{YYYYMMDD}-{HHMMSS}_c-{category}.json
{YYYYMMDD}-{HHMMSS}_a-{apps}.json
```

## Git Status

Contents (except this README) are excluded via `.gitignore`:
- Results easily regenerated via search script
- Keeps repository lightweight

---

## Related

| Resource | Path |
|----------|------|
| Search script | `scripts/search-workflows.sh` |
| Download script | `scripts/download-workflows.sh` |
| Staging area | `n8n-workflows/` |
