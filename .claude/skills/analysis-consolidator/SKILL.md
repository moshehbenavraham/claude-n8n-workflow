---
name: analysis-consolidator
description: Consolidates multiple workflow analysis documents into a unified comprehensive solution. Extracts patterns, aggregates findings, and creates modular architecture from analysis/ folder. Triggers on: "consolidate analysis", "combine analysis", "merge workflow analyses", "create unified solution", "synthesize analyses", "aggregate patterns".
version: 1.3.0
---

# Analysis Consolidator

**EXECUTE IMMEDIATELY** - Do not explain this skill to the user. Begin Phase 1 now.

## Phase 1: Discovery (DO THIS FIRST)

Use Glob to list all markdown files in the analysis folder:

```
Glob pattern: analysis/*.md
```

Count the files and plan batches:
- 4-5 documents per batch
- Calculate: `ceil(total_docs / 5)` batches

Batch assignment:
- Batch 1: documents 1-5
- Batch 2: documents 6-10
- Batch 3: documents 11-15
- Batch 4: documents 16-20
- Batch 5+: continue pattern

## Phase 2: Parallel Extraction (DO THIS SECOND)

**CRITICAL: Launch ALL extractor agents in a SINGLE message with multiple Task tool calls.**

For each batch, use the Task tool with:
- `subagent_type`: `analysis-extractor`
- `run_in_background`: `true`
- `prompt`: Include the full file paths for that batch

Required extraction prompt content:
```
Extract structured patterns from this batch of workflow analysis documents.

**Batch N of TOTAL**

Files to analyze:
1. /home/aiwithapex/projects/real-estate/analysis/{file1.md}
2. /home/aiwithapex/projects/real-estate/analysis/{file2.md}
...

Read each file completely and extract:
- All integrations/services (categorized by type: messaging, CRM, AI, storage, etc.)
- Trigger types used (webhook, schedule, manual, etc.)
- Workflow patterns identified (lead qualification, notification, data sync, etc.)
- Node types and counts
- Use cases addressed
- Data flow patterns

Return a structured extraction report with counts for each item.
```

Launch ALL batches in parallel in ONE message. Do not wait between batches.

## Phase 3: Collect Results (DO THIS THIRD)

Use AgentOutputTool to collect results from all background agents. Wait for ALL to complete before proceeding.

## Phase 4: Pattern Aggregation (DO THIS FOURTH)

Use the Task tool with:
- `subagent_type`: `pattern-aggregator`
- `prompt`: Must include ALL of the following:

Required aggregation prompt content:
```
Aggregate these extraction reports into a unified pattern analysis.

**Total Workflows Analyzed:** {N}

## Batch 1 Extraction Report
{paste complete Batch 1 results}

## Batch 2 Extraction Report
{paste complete Batch 2 results}

[... include ALL batches ...]

Your task:
1. Combine all data from every batch
2. Calculate total frequencies for each integration, trigger, pattern
3. Calculate coverage percentages (what % of workflows use each item)
4. Rank all items by frequency/importance
5. Identify pattern clusters (groups of items that appear together)
6. Produce a consolidated pattern analysis report with:
   - Ranked integrations with counts and coverage %
   - Ranked triggers with counts and coverage %
   - Ranked workflow patterns with counts and coverage %
   - Pattern clusters identified
   - Total unique items in each category
```

## Phase 5: Solution Architecture (DO THIS FIFTH)

**IMPORTANT: The solution-architect agent may hit token limits. Follow this approach:**

### Step 5a: Request CONCISE architecture output

Use the Task tool with:
- `subagent_type`: `solution-architect`
- `prompt`: Must include the following (note the CONCISE instruction):

Required architect prompt content:
```
Design a unified consolidated solution from this pattern analysis.

**Total Workflows Analyzed:** {N}
**Project Root:** /home/aiwithapex/projects/real-estate
**Output Path:** /home/aiwithapex/projects/real-estate/docs/consolidated-solution.md

## Consolidated Pattern Analysis (SUMMARY - key stats only)
- Top 5 integrations with coverage %
- Top 5 patterns with coverage %
- Recommended module count
- Target coverage %

{paste TOP-LEVEL STATS from aggregator - NOT the full verbose output}

**CRITICAL INSTRUCTIONS:**
1. Keep output UNDER 20,000 tokens to avoid token limits
2. Use the Write tool directly (NOT Bash with cat/heredoc)
3. Focus on actionable architecture, skip verbose explanations
4. Use tables instead of prose where possible
5. Limit code examples to essential snippets only

Create a focused solution document (~500 lines max) with:
- Executive Summary (10 lines max)
- Architecture Overview with ASCII diagram
- Module table (name, purpose, coverage, key integrations)
- Essential environment variables list
- 5-phase implementation roadmap (1 line per phase)
- Coverage matrix as compact table

Write using the Write tool to: docs/consolidated-solution.md
```

### Step 5b: Verify file was created

After the architect agent completes, IMMEDIATELY verify the file exists:
```bash
ls -la /home/aiwithapex/projects/real-estate/docs/consolidated-solution.md
```

### Step 5c: Fallback - Write directly if agent failed

**If the file does NOT exist after agent completion:**

This happens when the agent hits token limits or fails to execute writes.
YOU (the main agent) must write the file directly using the Write tool.

Use the aggregator output to create a consolidated solution with:
1. Executive summary with key stats from aggregator
2. Module list derived from pattern clusters
3. Coverage matrix from the aggregation
4. Basic implementation roadmap

Do NOT retry the solution-architect agent more than once - write directly on second failure.

## Phase 6: Verify and Report (DO THIS LAST)

1. Use Bash to verify file was created:
   ```bash
   ls -la /home/aiwithapex/projects/real-estate/docs/consolidated-solution.md
   ```

2. Report to user with:
   - Number of documents analyzed
   - Number of unique patterns identified
   - Number of unique integrations found
   - Estimated coverage percentage
   - Top 3-5 most common integrations
   - Top 3-5 most common patterns
   - Recommended modules from the solution
   - Output file location

## Batch Size Reference

| Total Docs | Batches |
|------------|---------|
| 1-5        | 1       |
| 6-10       | 2       |
| 11-15      | 3       |
| 16-20      | 4       |
| 21-25      | 5       |
| 26+        | ceil(n/5) |

## Error Handling

### Extractor Agent Failures
- If an extractor fails: retry that specific batch once, then continue without it
- Note missing batch in final report with affected workflow names

### Aggregator Agent Failures
- If aggregator fails: check extraction format, retry with simplified prompt
- If still fails: manually combine the top-level stats from each batch

### Architect Agent Failures (MOST COMMON)

**Token Limit Error:** `API Error: Claude's response exceeded the 32000 output token maximum`
- Do NOT retry with same prompt - it will fail again
- Instead: Write the document yourself using the Write tool directly
- Use aggregator stats to create a condensed version

**File Not Created Despite "Success":**
- Agent may show bash commands in output but not execute them
- Always verify with `ls -la` immediately after agent completes
- If file missing: write directly using Write tool (not Bash heredoc)

**General Architect Failures:**
1. First: ensure docs/ directory exists with `mkdir -p docs`
2. Second: retry with explicit instruction to use Write tool
3. Third: abandon agent, write file directly yourself

### Recovery Priority
1. **Never block on failed agents** - always have a fallback path
2. **Prefer Write tool over Bash** for file creation (more reliable)
3. **Condensed output > no output** - simpler doc is better than failed doc

## Quality Gates

- Final solution must cover >70% of analyzed workflows
- All extraction reports must be passed IN FULL to aggregator (no summarizing)
- Architect receives SUMMARY stats (not full verbose output) to avoid token limits
- **MANDATORY: Verify output file exists with `ls -la` before reporting success**
- **MANDATORY: If file missing, write directly - do not report success without file**

---

**START NOW: Run Glob to discover analysis files, then immediately launch parallel extractors.**
