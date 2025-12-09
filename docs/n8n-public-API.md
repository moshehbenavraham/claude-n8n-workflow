# n8n Public Templates API Documentation

Complete reference for the n8n public workflow templates API at `api.n8n.io`.

## Base URL

```
https://api.n8n.io/api/templates
```

## Authentication

The public templates API requires **no authentication**. All endpoints are publicly accessible.

## Rate Limiting

No explicit rate limits are documented. The API uses Cloudflare caching with a `max-age=14400` (4 hours) cache header.

## Response Format

All responses are JSON with UTF-8 encoding.

**Success Response:**
```json
{
  "field": "value"
}
```

**Error Response:**
```json
{
  "data": null,
  "error": {
    "status": 400,
    "name": "BadRequestError",
    "message": "Error description",
    "details": {}
  }
}
```

---

## Endpoints

### 1. Health Check

Check API status.

```
GET /api/health
```

**Response:**
```json
{
  "status": "OK"
}
```

---

### 2. List Workflows

Retrieve all workflow templates with pagination.

```
GET /api/templates/workflows
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rows` | integer | 10 | Number of workflows to return |
| `skip` | integer | 0 | Number of workflows to skip (pagination offset) |

**Example:**
```bash
curl "https://api.n8n.io/api/templates/workflows?rows=5&skip=10"
```

**Response:**
```json
{
  "totalWorkflows": 7285,
  "workflows": [
    {
      "id": 5428,
      "name": "Workflow Name",
      "totalViews": 12345,
      "recentViews": 100,
      "price": 0,
      "purchaseUrl": null,
      "createdAt": "2024-01-15T10:30:00.000Z",
      "user": {
        "id": 12345,
        "name": "Author Name",
        "username": "authorusername",
        "bio": "Author bio text",
        "verified": true,
        "links": "[\"https://example.com\"]",
        "avatar": "https://gravatar.com/avatar/..."
      },
      "nodes": [
        {
          "id": 19,
          "icon": "file:httprequest.svg",
          "name": "n8n-nodes-base.httpRequest",
          "displayName": "HTTP Request",
          "typeVersion": 1,
          "group": "[\"output\"]",
          "defaults": {
            "name": "HTTP Request",
            "color": "#0004F5"
          },
          "nodeCategories": [
            {"id": 3, "name": "Development"}
          ],
          "codex": {
            "data": {
              "alias": ["API", "Request"],
              "categories": ["Development", "Core Nodes"],
              "resources": {}
            }
          }
        }
      ],
      "description": "Full workflow description..."
    }
  ]
}
```

---

### 3. Get Single Workflow

Retrieve complete workflow details including the importable workflow JSON.

```
GET /api/templates/workflows/{id}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Workflow template ID |

**Example:**
```bash
curl "https://api.n8n.io/api/templates/workflows/5428"
```

**Response Structure:**
```json
{
  "workflow": {
    "id": 5428,
    "name": "Workflow Name",
    "views": 12345,
    "recentViews": 100,
    "totalViews": 12345,
    "createdAt": "2024-01-15T10:30:00.000Z",
    "description": "Full description...",
    "status": "published",
    "lastUpdatedBy": 12345,

    "user": {
      "name": "Author Name",
      "username": "authorusername",
      "bio": "Author bio",
      "verified": true,
      "links": [],
      "avatar": "https://gravatar.com/avatar/..."
    },

    "workflowInfo": {
      "nodeCount": 12,
      "nodeTypes": {
        "n8n-nodes-base.httpRequest": 3,
        "n8n-nodes-base.set": 2
      }
    },

    "nodes": [
      {
        "id": 19,
        "icon": "file:httprequest.svg",
        "name": "n8n-nodes-base.httpRequest",
        "displayName": "HTTP Request",
        "typeVersion": 1,
        "group": "[\"output\"]",
        "defaults": {},
        "codex": {},
        "nodeCategories": []
      }
    ],

    "categories": [
      {"id": 25, "name": "AI"}
    ],

    "image": [],

    "workflow": {
      "id": "gFQYkoSGHEW9QiCU",
      "name": "Workflow Name",
      "active": false,
      "versionId": "uuid-string",
      "meta": {
        "instanceId": "instance-id",
        "templateCredsSetupCompleted": true
      },
      "settings": {
        "executionOrder": "v1"
      },
      "pinData": {},
      "tags": [],
      "nodes": [
        {
          "id": "uuid-string",
          "name": "Node Name",
          "type": "n8n-nodes-base.nodeType",
          "typeVersion": 2.2,
          "position": [250, 300],
          "parameters": {},
          "credentials": {},
          "webhookId": "optional-webhook-id"
        }
      ],
      "connections": {
        "Node Name": {
          "main": [
            [{"node": "Next Node", "type": "main", "index": 0}]
          ]
        }
      }
    }
  }
}
```

**Important:** The nested `workflow.workflow` object contains the importable workflow JSON for n8n.

---

### 4. Search Workflows

Search and filter workflow templates with faceted filters.

```
GET /api/templates/search
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | - | Search query string |
| `rows` | integer | 10 | Number of results to return |
| `skip` | integer | 0 | Pagination offset |
| `category` | string | - | Filter by category name(s), comma-separated |
| `apps` | string | - | Filter by app/integration names, comma-separated |
| `nodes` | string | - | Filter by node type names, comma-separated |
| `nApps` | integer | 10 | Number of app filter counts to return |
| `nCategories` | integer | 10 | Number of category filter counts to return |

**Examples:**
```bash
# Basic search
curl "https://api.n8n.io/api/templates/search?search=telegram&rows=5"

# Filter by category
curl "https://api.n8n.io/api/templates/search?category=AI"

# Multiple filters
curl "https://api.n8n.io/api/templates/search?search=openai&apps=Telegram,OpenAI&rows=10"

# Filter by specific node type
curl "https://api.n8n.io/api/templates/search?nodes=n8n-nodes-base.telegram"
```

**Response:**
```json
{
  "totalWorkflows": 971,
  "workflows": [
    {
      "id": 5428,
      "name": "Workflow Name",
      "totalViews": 12345,
      "price": 0,
      "purchaseUrl": null,
      "createdAt": "2024-01-15T10:30:00.000Z",
      "user": {},
      "nodes": [],
      "description": "..."
    }
  ],
  "filters": [
    {
      "field_name": "categories",
      "sampled": false,
      "stats": {"total_values": 31},
      "counts": [
        {"count": 4836, "value": "AI", "highlighted": "AI"},
        {"count": 2565, "value": "Multimodal AI", "highlighted": "Multimodal AI"}
      ]
    },
    {
      "field_name": "apps",
      "sampled": false,
      "stats": {"total_values": 100},
      "counts": [
        {"count": 4534, "value": "Sticky Note"},
        {"count": 2468, "value": "Edit Fields (Set)"}
      ]
    },
    {
      "field_name": "nodes",
      "sampled": false,
      "stats": {"total_values": 200},
      "counts": [
        {"count": 4534, "value": "n8n-nodes-base.stickyNote"}
      ]
    }
  ]
}
```

---

### 5. List Categories

Retrieve all workflow categories with hierarchy.

```
GET /api/templates/categories
```

**Example:**
```bash
curl "https://api.n8n.io/api/templates/categories"
```

**Response:**
```json
{
  "categories": [
    {
      "id": 25,
      "name": "AI",
      "displayName": null,
      "icon": "sparkles",
      "parent": null
    },
    {
      "id": 47,
      "name": "AI Chatbot",
      "displayName": "AI Chatbot, Assistant, Agent",
      "icon": "label",
      "parent": {
        "id": 25,
        "name": "AI",
        "icon": "sparkles"
      }
    },
    {
      "id": 48,
      "name": "AI RAG",
      "displayName": "AI RAG, MCP & Knowledge Retrieval",
      "icon": "label",
      "parent": {
        "id": 25,
        "name": "AI",
        "icon": "sparkles"
      }
    }
  ]
}
```

**Category Hierarchy (as of December 2025):**

| Parent | Subcategories |
|--------|---------------|
| **AI** | AI Chatbot, AI RAG, AI Summarization, Multimodal AI |
| **Marketing** | Content Creation, Market Research, Social Media |
| **Sales** | CRM, Lead Generation, Lead Nurturing |
| **IT Ops** | DevOps, Engineering, SecOps |
| **Document Ops** | Document Extraction, File Management, Invoice Processing |
| **Support** | Internal Wiki, Support Chatbot, Ticket Management |
| **Other** | Crypto Trading, HR, Miscellaneous, Personal Productivity, Project Management |

---

### 6. List Collections

Retrieve curated workflow collections.

```
GET /api/templates/collections
```

**Example:**
```bash
curl "https://api.n8n.io/api/templates/collections"
```

**Response:**
```json
{
  "collections": [
    {
      "id": 7,
      "rank": 0,
      "name": "n8n Key Concepts",
      "totalViews": 0,
      "createdAt": "2022-07-06T14:51:53.250Z",
      "workflows": [
        {"id": 1700},
        {"id": 1744}
      ],
      "nodes": []
    },
    {
      "id": 8,
      "rank": 1,
      "name": "Advanced AI",
      "totalViews": null,
      "createdAt": "2023-10-03T17:04:44.645Z",
      "workflows": [
        {"id": 1951},
        {"id": 1953}
      ],
      "nodes": []
    }
  ]
}
```

**Available Collections:**

| ID | Name | Workflow Count |
|----|------|----------------|
| 7 | n8n Key Concepts | 8 |
| 8 | Advanced AI | 32 |
| 9 | Cybersecurity | 10 |
| 1 | eCommerce Starter Pack | 6 |
| 4 | Invoicing and Accounting Starter Pack | 4 |
| 6 | Managed Service Provider Starter Pack | 6 |
| 3 | Marketing/Growth Starter Pack | 7 |
| 5 | Teamwork Starter Pack | 6 |

---

### 7. Get Single Collection

Retrieve a specific collection with full workflow details.

```
GET /api/templates/collections/{id}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Collection ID |

**Example:**
```bash
curl "https://api.n8n.io/api/templates/collections/8"
```

**Response:**
```json
{
  "collection": {
    "id": 8,
    "name": "Advanced AI",
    "description": "n8n allows you to build powerful AI automations...",
    "totalViews": null,
    "createdAt": "2023-10-03T17:04:44.645Z",
    "nodes": [],
    "categories": [],
    "workflows": [
      {
        "id": 1954,
        "name": "AI agent chat",
        "views": 1162041,
        "recentViews": 18,
        "totalViews": 1162041,
        "createdAt": "2023-10-03T14:49:21.377Z",
        "description": "...",
        "status": "published",
        "user": {},
        "nodes": [],
        "categories": [],
        "workflow": {
          "meta": {},
          "nodes": [],
          "pinData": {},
          "connections": {}
        },
        "workflowInfo": {
          "nodeCount": 10,
          "nodeTypes": {}
        }
      }
    ]
  }
}
```

---

## Pagination

The API uses offset-based pagination with `rows` and `skip` parameters:

```bash
# Page 1 (first 10 results)
curl "https://api.n8n.io/api/templates/workflows?rows=10&skip=0"

# Page 2 (results 11-20)
curl "https://api.n8n.io/api/templates/workflows?rows=10&skip=10"

# Page 3 (results 21-30)
curl "https://api.n8n.io/api/templates/workflows?rows=10&skip=20"
```

Use `totalWorkflows` from the response to calculate total pages.

---

## Common Use Cases

### Download a Workflow JSON

Extract the importable workflow object:

```bash
curl -s "https://api.n8n.io/api/templates/workflows/5428" | \
  jq '.workflow.workflow' > workflow-5428.json
```

### Batch Download Multiple Workflows

```bash
#!/bin/bash
ids=(5428 6332 6162 4281)

for id in "${ids[@]}"; do
  curl -s "https://api.n8n.io/api/templates/workflows/$id" | \
    jq '.workflow.workflow' > "workflow-$id.json"
  echo "Downloaded workflow $id"
done
```

### Search Real Estate Workflows

```bash
curl -s "https://api.n8n.io/api/templates/search?search=real+estate&rows=20" | \
  jq '.workflows[] | {id, name, totalViews}'
```

### Get All AI Category Workflows

```bash
curl -s "https://api.n8n.io/api/templates/search?category=AI&rows=100" | \
  jq '.totalWorkflows'
```

### Paginate Through All Workflows

```bash
#!/bin/bash
skip=0
rows=100

while true; do
  response=$(curl -s "https://api.n8n.io/api/templates/workflows?rows=$rows&skip=$skip")
  count=$(echo "$response" | jq '.workflows | length')

  if [ "$count" -eq 0 ]; then
    break
  fi

  echo "$response" | jq '.workflows[] | {id, name}'
  skip=$((skip + rows))
done
```

---

## Data Types Reference

### Workflow Object (List)

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | integer | No | Unique workflow ID |
| name | string | No | Workflow title |
| totalViews | integer | No | All-time view count |
| recentViews | integer | Yes | Recent view count |
| price | number | Yes | Price (0 = free) |
| purchaseUrl | string | Yes | Purchase link if paid |
| createdAt | string | No | ISO 8601 timestamp |
| description | string | No | Full description (markdown) |
| user | object | No | Author information |
| nodes | array | No | Node type metadata |

### User Object

| Field | Type | Description |
|-------|------|-------------|
| id | integer | User ID |
| name | string | Display name |
| username | string | Unique username |
| bio | string | Profile bio |
| verified | boolean | Verification status |
| links | string | JSON array of social links |
| avatar | string | Gravatar URL |

### Category Object

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Category ID |
| name | string | Internal name |
| displayName | string | Human-readable name (nullable) |
| icon | string | Emoji or icon identifier |
| parent | object | Parent category (nullable) |

### Collection Object

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Collection ID |
| rank | integer | Display order |
| name | string | Collection name |
| description | string | Collection description |
| totalViews | integer | View count (nullable) |
| createdAt | string | ISO 8601 timestamp |
| workflows | array | Array of workflow objects or IDs |
| nodes | array | Featured nodes (usually empty) |

---

## Error Codes

| Status | Name | Description |
|--------|------|-------------|
| 400 | BadRequestError | Invalid request parameters |
| 404 | Not Found | Resource doesn't exist (returns 400) |

Note: Non-existent resources return HTTP 200 with error body containing status 400.

---

## Response Headers

| Header | Value | Description |
|--------|-------|-------------|
| Content-Type | application/json; charset=utf-8 | Response format |
| Cache-Control | max-age=14400 | 4-hour cache |
| X-Powered-By | n8n <n8n.io> | Server identifier |

---

## Environment Variables

When self-hosting or embedding n8n templates:

```bash
# Point to custom template API
N8N_TEMPLATES_HOST=https://your-api.example.com
```

Your custom API must implement the same endpoints and data structures.

---

## References

- [n8n Workflows Library](https://n8n.io/workflows/)
- [n8n Templates Documentation](https://docs.n8n.io/workflows/templates/)
- [n8n Embedded Templates](https://docs.n8n.io/embed/workflow-templates/)
- [n8n Public REST API](https://docs.n8n.io/api/)
