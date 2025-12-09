# n8n Node Types Reference

Comprehensive documentation of common n8n node types encountered in workflows.

## Trigger Nodes

Entry points that start workflow execution.

### webhook
**Type:** `n8n-nodes-base.webhook`

Receives HTTP requests to trigger workflows.

**Key Parameters:**
- `httpMethod`: GET, POST, PUT, DELETE, etc.
- `path`: URL path for the webhook endpoint
- `responseMode`: onReceived, lastNode, responseNode
- `authentication`: none, basicAuth, headerAuth

**Data Output:**
```json
{
  "headers": {},
  "params": {},
  "query": {},
  "body": {}
}
```

### schedule
**Type:** `n8n-nodes-base.scheduleTrigger`

Triggers workflows on a schedule (cron).

**Key Parameters:**
- `rule`: Cron expression or interval
- `timezone`: Execution timezone

### manualTrigger
**Type:** `n8n-nodes-base.manualTrigger`

Triggered manually for testing.

## Data Processing Nodes

### httpRequest
**Type:** `n8n-nodes-base.httpRequest`

Makes HTTP requests to external APIs.

**Key Parameters:**
- `url`: Target URL (supports expressions)
- `method`: HTTP method
- `authentication`: Various auth types
- `sendHeaders`: Custom headers
- `sendBody`: Request body configuration
- `options.response.response.responseFormat`: json, text, file

**Analysis Tips:**
- Check URL for API identification
- Look for `={{` expressions for dynamic values
- Note authentication method for credential requirements

### code
**Type:** `n8n-nodes-base.code`

Executes custom JavaScript or Python code.

**Key Parameters:**
- `jsCode`: JavaScript code string
- `pythonCode`: Python code string
- `mode`: runOnceForAllItems, runOnceForEachItem

**Common Patterns in Code:**
```javascript
// Access input data
const items = $input.all();
const firstItem = $input.first();
const json = $input.first().json;

// Access previous node data
const prevData = $('NodeName').first().json;

// Return data
return { field: value };
return items.map(item => ({ json: { ...item.json, newField: value }}));
```

**Analysis Tips:**
- Look for business logic (scoring, filtering, transformation)
- Identify external API calls within code
- Note error handling patterns

### set
**Type:** `n8n-nodes-base.set`

Sets field values on items.

**Key Parameters:**
- `values`: Array of field assignments
- `options.dotNotation`: Enable nested field access
- `mode`: manual, raw

### function (Legacy)
**Type:** `n8n-nodes-base.function`

Legacy code execution node (replaced by code node).

## Conditional Nodes

### if
**Type:** `n8n-nodes-base.if`

Binary conditional branching.

**Key Parameters:**
- `conditions`: Condition configuration
  - `value1`: Left operand
  - `operation`: Comparison operator
  - `value2`: Right operand

**Outputs:**
- Output 0: True branch
- Output 1: False branch

### switch
**Type:** `n8n-nodes-base.switch`

Multi-way branching based on value matching.

**Key Parameters:**
- `dataType`: string, number, boolean
- `value1`: Value to test
- `rules`: Array of matching rules

### filter
**Type:** `n8n-nodes-base.filter`

Filters items based on conditions.

## Data Combination Nodes

### merge
**Type:** `n8n-nodes-base.merge`

Combines data from multiple inputs.

**Modes:**
- `append`: Concatenate all items
- `multiplex`: Cartesian product
- `chooseBranch`: Select specific input
- `mergeByKey`: Join by field value

### splitInBatches
**Type:** `n8n-nodes-base.splitInBatches`

Splits input into batches for processing.

**Key Parameters:**
- `batchSize`: Items per batch
- `options.reset`: Reset on workflow restart

## Utility Nodes

### noOp
**Type:** `n8n-nodes-base.noOp`

No operation - passes data through unchanged. Used for flow organization.

### stickyNote
**Type:** `n8n-nodes-base.stickyNote`

Documentation node - NOT executed.

**Key Parameters:**
- `content`: Note text (often markdown)
- `height`, `width`: Display dimensions
- `color`: Note color for visual organization

**Analysis Note:** Contains embedded documentation from workflow author.

### wait
**Type:** `n8n-nodes-base.wait`

Pauses execution for specified duration.

### respondToWebhook
**Type:** `n8n-nodes-base.respondToWebhook`

Sends response to webhook trigger.

## Integration Nodes

### slack
**Type:** `n8n-nodes-base.slack`

Slack integration.

**Common Operations:**
- `postMessage`: Send message to channel
- `upload`: Upload file
- `getUser`: Get user info

### discord
**Type:** `n8n-nodes-base.discord`

Discord integration.

### email / gmail / sendGrid
Email sending nodes with various providers.

### airtable / googleSheets / notion
Spreadsheet/database integrations.

## Database Nodes

### postgres / mysql / mongodb
Direct database connections.

**Key Parameters:**
- `operation`: select, insert, update, delete
- `query`: SQL/query string
- `options`: Connection settings

## Error Handling

### errorTrigger
**Type:** `n8n-nodes-base.errorTrigger`

Triggers when another workflow errors.

### stopAndError
**Type:** `n8n-nodes-base.stopAndError`

Stops workflow execution with error.

## Common Parameter Patterns

### Expressions
n8n uses `={{...}}` syntax for dynamic values:
```
={{ $json.fieldName }}
={{ $input.first().json.data }}
={{ $('NodeName').first().json.result }}
={{ $now.format('YYYY-MM-DD') }}
```

### Credentials
Nodes reference credentials by name:
```json
{
  "credentials": {
    "slackApi": {
      "id": "1",
      "name": "Slack Account"
    }
  }
}
```

### Options
Many nodes have an `options` object for advanced settings:
```json
{
  "options": {
    "timeout": 30000,
    "retry": true,
    "batching": { "batch": { "batchSize": 10 }}
  }
}
```

## Identifying Node Purpose

1. **Check the name** - Authors usually name nodes descriptively
2. **Check the type** - Indicates general category
3. **Check parameters** - URL, query, code reveal specifics
4. **Check position** - Context from surrounding nodes
5. **Check connections** - Input/output relationships
