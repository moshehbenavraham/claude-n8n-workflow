# Workflow Analysis: Real Estate Property Search with SQL Database and Email Delivery

## Quick Summary

This workflow provides a complete self-service property search portal that captures user preferences via web form, dynamically queries a SQL Server database of 1000+ real US properties, and delivers personalized results via email with an attached CSV spreadsheet. It enables 24/7 automated lead generation for real estate professionals.

## Workflow Diagram

```
┌─────────────────────────┐
│   Property Search Form  │  (Web Form Trigger)
│   - Email address       │
│   - Price range         │
│   - Bedrooms/Bathrooms  │
│   - Location filters    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    Build SQL Query      │  (Code Node)
│   - Dynamic WHERE       │
│   - Only filled fields  │
│   - Numeric ranges      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    Microsoft SQL        │  (Database Query)
│   - Execute query       │
│   - Return properties   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    Convert to File      │  (CSV Generator)
│   - Transform to CSV    │
│   - Excel-ready format  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    Send a message       │  (Gmail)
│   - Personalized email  │
│   - Top 3 previews      │
│   - CSV attachment      │
└─────────────────────────┘
```

## Purpose & Use Cases

### Primary Purpose
Transform property searches into personalized client experiences by delivering matching properties straight to clients' inboxes with professional CSV reports from a simple web form.

### Target Users
- **Real Estate Agents** - Generate leads and impress clients with instant service
- **Property Managers** - Automate tenant matching and recommendations
- **Brokerages** - Provide 24/7 self-service property discovery
- **Real Estate Developers** - Showcase available properties with professional automation

### Key Benefits
- Instant results (under 30 seconds from search to delivery)
- Professional output that showcases expertise
- Mobile-optimized form works on all devices
- Smart filtering only searches specified criteria
- Infinitely scalable for unlimited simultaneous searches

## Technical Architecture

### Entry Point

**Property Search Form** (`n8n-nodes-base.formTrigger`)
- Webhook path: `/property-search-form`
- Form title: "Find Your Perfect Property"
- 14 input fields capturing comprehensive search criteria

| Field | Type | Required |
|-------|------|----------|
| Your Email Address | email | Yes |
| Property Status | select | No |
| Minimum Price ($) | number | No |
| Maximum Price ($) | number | No |
| Minimum Bedrooms | number | No |
| Maximum Bedrooms | number | No |
| Minimum Bathrooms | number | No |
| Maximum Bathrooms | number | No |
| Minimum House Size (sqft) | number | No |
| Maximum House Size (sqft) | number | No |
| Minimum Lot Size (acres) | number | No |
| State | text | No |
| City | text | No |
| ZIP Code | text | No |

### Processing Pipeline

#### 1. Build SQL Query (Code Node)
Dynamically constructs SQL queries based on user input:

**Logic Highlights:**
- Only adds WHERE conditions for fields the user actually filled
- Handles numeric range conditions (min/max) for price, beds, baths, size
- Sanitizes string inputs for state, city, status
- Converts ZIP code to integer
- Returns TOP 1000 results ordered by price ascending

**Output Structure:**
```javascript
{
  query: "SELECT ... FROM [REALTOR].[dbo].[realtor_usa_price] WHERE ...",
  searchCriteria: { priceRange, bedrooms, bathrooms, location, ... },
  formData: { /* original form data */ },
  userEmail: "user@example.com",
  searchTimestamp: "2025-..."
}
```

#### 2. Microsoft SQL (Database Query)
- Executes the dynamically built query
- Queries table: `[REALTOR].[dbo].[realtor_usa_price]`
- Returns matching property records

#### 3. Convert to File (CSV Generator)
- Transforms database results into CSV format
- Excel-ready output for easy client review

#### 4. Send a message (Gmail)
- Sends personalized email to the user's submitted email address
- Subject: Dynamic count of properties found
- Body includes:
  - Greeting with total match count
  - Top 3 property previews (price, beds/baths, location)
  - Search criteria summary
  - CSV file attachment

### Database Schema

Table: `[REALTOR].[dbo].[realtor_usa_price]`

| Column | Type | Description |
|--------|------|-------------|
| brokered_by | BIGINT | Broker identifier |
| status | NVARCHAR(50) | Property status (active, sold, etc.) |
| price | DECIMAL(12,2) | Listing price |
| bed | INT | Number of bedrooms |
| bath | DECIMAL(3,1) | Number of bathrooms |
| acre_lot | DECIMAL(10,8) | Lot size in acres |
| street | BIGINT | Street identifier |
| city | NVARCHAR(100) | City name |
| state | NVARCHAR(50) | State name |
| zip_code | INT | ZIP code |
| house_size | INT | House size in sqft |
| prev_sold_date | NVARCHAR(50) | Previous sale date |

## Implementation Requirements

### External Services

| Service | Purpose |
|---------|---------|
| Microsoft SQL Server | Property database storage |
| Gmail API | Email delivery |
| n8n Instance | Workflow automation |

### Credentials Required

1. **Microsoft SQL Server Credentials**
   - Server hostname/IP
   - Database name (REALTOR)
   - Username and password
   - Port (default 1433)

2. **Gmail OAuth2 Credentials**
   - Google Cloud Console project
   - Gmail API enabled
   - OAuth2 client credentials
   - Authorized redirect URI for n8n

### Configuration Steps

#### Step 1: Import Real Estate Data
1. Download data from [GitHub repository](https://github.com/dataminexcode/n8n-workflow/tree/main/Real%20Estate%20Property%20Search%20with%20SQL%20Database%20and%20Email%20Delivery/data)
2. Create SQL Server table with the schema above
3. Import CSV data (1000+ properties included)

#### Step 2: Configure Database Connection
1. Set up Microsoft SQL Server credentials in n8n
2. Test connection to ensure connectivity
3. Verify table access and data availability

#### Step 3: Gmail Setup
1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or use existing
3. Enable Gmail API in API Library
4. Create OAuth2 credentials (Web Application)
5. Add n8n callback URL to authorized redirects
6. Configure Gmail OAuth2 credentials in n8n
7. Authorize your Google account

#### Step 4: Launch Property Search Portal
1. Import this workflow template
2. Copy webhook URL from Property Search Form node
3. Test with sample property search
4. Verify email delivery with CSV attachment
5. Go live

## Node Details

| # | Node Name | Type | Purpose |
|---|-----------|------|---------|
| 1 | Property Search Form | formTrigger | Entry point - captures user search criteria via web form |
| 2 | Build SQL Query | code | Dynamically constructs SQL query from form input |
| 3 | Microsoft SQL | microsoftSql | Executes query against property database |
| 4 | Convert to File | convertToFile | Transforms results to CSV format |
| 5 | Send a message | gmail | Delivers personalized email with CSV attachment |

**Documentation Nodes (5 sticky notes):**
- Sticky Note: "START HERE!" - Entry point guidance
- Sticky Note1: "SMART QUERY BUILDER" - Code node explanation
- Sticky Note2: "DATABASE DETECTIVE" - SQL node explanation
- Sticky Note3: "EXCEL MAGIC" - CSV conversion explanation
- Sticky Note4: "DELIVERY SERVICE" - Email delivery explanation

## Data Flow Description

### Input
User submits web form with property search preferences:
- Contact email (required)
- Optional filters: price range, bedroom/bathroom counts, size, location

### Transformation
1. **Form → Query Builder**: Raw form data transformed to dynamic SQL query
2. **Query → Database**: SQL executed, returns matching property records
3. **Records → CSV**: Property data converted to spreadsheet format
4. **CSV → Email**: Results packaged into personalized email with attachment

### Output
- Personalized email sent to user
- Subject with property count
- Top 3 property previews in email body
- Complete results as CSV attachment

## Customization Guide

### Easy Modifications

**Email Subject Customization:**
```javascript
// Examples from author:
"Exclusive Properties Curated Just for You - ${results.length} Perfect Matches!"
"Your Dream Home Portfolio - Handpicked by Our Experts"
"Hot Market Alert - ${results.length} Premium Properties Inside!"
```

**Database Switching:**
- MySQL: Replace Microsoft SQL node with MySQL node
- PostgreSQL: Swap for PostgreSQL node
- MongoDB: Use MongoDB node with JSON queries
- CSV files: Use CSV reading nodes for smaller datasets

### Advanced Enhancements

| Enhancement | Description |
|-------------|-------------|
| HTML Email Templates | Create stunning visual emails with property images |
| Analytics Dashboard | Track popular searches and user engagement |
| Smart Alerts | Automated price drop notifications |
| Mobile Integration | Connect to React Native or Flutter apps |
| AI Descriptions | Add ChatGPT for compelling property descriptions |
| CRM Connection | Auto-add qualified leads to your CRM |
| Calendar Integration | Add property viewing scheduling |
| SMS/WhatsApp | Instant text alerts for hot properties |

### Security Considerations

**Note:** The current SQL query builder uses string interpolation which could be vulnerable to SQL injection. For production use, consider:
- Input validation on all form fields
- Parameterized queries instead of string concatenation
- Rate limiting on the webhook endpoint

## Metadata

| Field | Value |
|-------|-------|
| Workflow ID | 7329 |
| Author | DataMinex (verified) |
| Created | August 13, 2025 |
| Views | 1,420 |
| Categories | Lead Nurturing, Multimodal AI |
| Node Count | 10 (5 execution + 5 documentation) |
| Status | Published |

## Related Resources

- [Sample Data Repository](https://github.com/dataminexcode/n8n-workflow/tree/main/Real%20Estate%20Property%20Search%20with%20SQL%20Database%20and%20Email%20Delivery/data)
- [Author Website](https://dataminex.org/)
