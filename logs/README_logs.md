# Logs

Script execution logs and debug output.

---

## Purpose

Storage for log files generated during workflow download, split, and analysis operations.

---

## Expected Contents

| Log Type | Source |
|----------|--------|
| Download logs | `download-workflows.sh` verbose output |
| Split logs | `split-workflows.sh` processing output |
| API responses | Raw API response data for debugging |
| Error logs | Failed operations and stack traces |

---

## Retention

Log files in this directory are typically:
- Excluded from version control via `.gitignore`
- Safe to delete after debugging
- Generated fresh on each script run

Do not .gitignore this README file.

---

## Related

| Resource | Path |
|----------|------|
| Scripts | `scripts/` |
