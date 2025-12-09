# n8n Workflow Analysis Patterns

Common workflow patterns and how to identify and analyze them.

## Common Workflow Architectures

### 1. API Enrichment Pipeline

**Pattern:**
```
[Trigger] -> [Fetch Original Data] -> [Call Enrichment API] -> [Process/Score] -> [Update/Store]
```

**Identification:**
- Multiple httpRequest nodes in sequence
- Code node for data processing/scoring
- Final httpRequest for updating source system

**Example Use Cases:**
- Lead enrichment (add company data to contacts)
- Property data lookup (add property details to leads)
- Email verification workflows

**Analysis Focus:**
- What data comes in?
- What APIs are called for enrichment?
- What scoring/processing logic is applied?
- Where is enriched data stored?

### 2. Conditional Routing

**Pattern:**
```
[Trigger] -> [Process] -> [IF/Switch] -+-> [Action A]
                                       +-> [Action B]
                                       +-> [Action C]
```

**Identification:**
- `if` or `switch` node after processing
- Multiple terminal branches
- Different actions per condition

**Example Use Cases:**
- Lead qualification (route by score)
- Support ticket routing (route by priority)
- Multi-channel notifications

**Analysis Focus:**
- What conditions determine routing?
- What happens in each branch?
- Are there fallback/default paths?

### 3. Fan-Out/Fan-In (Parallel Processing)

**Pattern:**
```
[Trigger] -> [Split] -+-> [Process A] -+-> [Merge] -> [Final]
                      +-> [Process B] -+
                      +-> [Process C] -+
```

**Identification:**
- Single node connecting to multiple nodes
- Merge node collecting results
- Parallel API calls or processing

**Example Use Cases:**
- Multi-source data aggregation
- Parallel API calls to different services
- Batch processing with parallel workers

**Analysis Focus:**
- Why is parallel processing needed?
- What merging strategy is used?
- How are failures in branches handled?

### 4. Webhook Response Pipeline

**Pattern:**
```
[Webhook] -> [Process] -> [Format Response] -> [Respond to Webhook]
```

**Identification:**
- Webhook trigger with responseMode: responseNode
- respondToWebhook node at end
- Processing/validation in between

**Example Use Cases:**
- API endpoint implementation
- Form submission handling
- Real-time data validation

**Analysis Focus:**
- What does the webhook expect as input?
- What validation/processing occurs?
- What response format is returned?

### 5. Scheduled Batch Processing

**Pattern:**
```
[Schedule] -> [Fetch Batch] -> [Loop/Split] -> [Process Each] -> [Aggregate/Report]
```

**Identification:**
- Schedule trigger (cron)
- Data fetching from source
- splitInBatches or loop pattern
- Final aggregation/notification

**Example Use Cases:**
- Daily report generation
- Batch data synchronization
- Scheduled cleanup tasks

**Analysis Focus:**
- What schedule/frequency?
- What batch size is used?
- How are errors in batch items handled?

### 6. Error Recovery Pattern

**Pattern:**
```
[Main Flow] --(error)--> [Error Handler] -> [Log/Notify] -> [Retry/Cleanup]
```

**Identification:**
- Error trigger node
- Notification on failure
- Possible retry logic

**Example Use Cases:**
- Critical workflow monitoring
- Automatic retry with backoff
- Alert on failures

**Analysis Focus:**
- What errors are caught?
- What notification is sent?
- Is there retry logic?

## Identifying Workflow Purpose

### Step 1: Examine Trigger
| Trigger Type | Typical Purpose |
|--------------|-----------------|
| Webhook | Real-time event processing |
| Schedule | Batch/periodic tasks |
| Manual | Testing or on-demand |
| App trigger (Slack, etc.) | Reactive to external events |

### Step 2: Count & Categorize Nodes
| Node Mix | Likely Purpose |
|----------|----------------|
| Many httpRequest | API integration/orchestration |
| Many code | Complex business logic |
| Many if/switch | Decision routing |
| Many integration nodes | Multi-platform sync |

### Step 3: Trace Data Flow
1. What enters the workflow?
2. What transformations occur?
3. What exits the workflow?

### Step 4: Check Sticky Notes
Authors often explain:
- Why the workflow exists
- Who should use it
- What customization is needed

## Red Flags to Note

### Security Concerns
- Hardcoded API keys in code nodes
- No input validation on webhooks
- Sensitive data in URLs (query params)

### Reliability Concerns
- No error handling
- Missing timeout configuration
- No retry logic on API calls

### Maintainability Concerns
- No documentation (sticky notes)
- Magic numbers in code
- Unnamed nodes

### Performance Concerns
- Sequential calls that could be parallel
- Missing batch processing for large datasets
- No rate limiting consideration

## Analysis Output Templates

### Quick Summary Template
```markdown
**Workflow:** {Name}
**Purpose:** {One-line description}
**Trigger:** {How it starts}
**Main Flow:** {Entry} -> {Process} -> {Output}
**Integrations:** {List of external services}
```

### Detailed Analysis Template
```markdown
## {Workflow Name}

### Overview
{2-3 sentence description}

### Architecture Pattern
{Pattern name from above}

### Data Flow
1. **Input:** {What triggers and what data}
2. **Processing:** {What happens to data}
3. **Output:** {What is produced/updated}

### External Dependencies
| Service | Purpose | Required Credentials |
|---------|---------|---------------------|

### Configuration Requirements
- {Requirement 1}
- {Requirement 2}

### Customization Points
- {What can be easily changed}

### Notes/Concerns
- {Any issues identified}
```

## Questions to Answer in Analysis

1. **What problem does this solve?**
2. **Who would use this workflow?**
3. **What external services are required?**
4. **What credentials/API keys are needed?**
5. **What is the happy path flow?**
6. **What error handling exists?**
7. **What customization is possible?**
8. **What are the limitations?**
