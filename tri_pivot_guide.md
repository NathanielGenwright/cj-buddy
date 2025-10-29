# TRI Dataset - Pivot Table Guide

**Export Date**: 2025-10-13 18:23:08  
**Total Fields**: 20  
**Reference Ticket**: TRI-1858  

## 📊 Quick Pivot Suggestions

- Status vs Category_From_Summary (workflow by business area)
- Assignee vs Issue_Category (workload by request type)
- Client_CID vs Status (client ticket tracking)
- Contains_Emergency_Keywords vs Status (urgent ticket handling)
- Category_From_Summary vs Count (business area volume)

## 🔍 Field Descriptions

### Standard Fields

| Field | Description |
|-------|-------------|
| Ticket_Key | JIRA ticket identifier (TRI-XXXX) |
| Summary | Ticket summary/title text |
| Issue_Type | JIRA issue type (usually [System] Service request) |
| Status | Current workflow status |
| Assignee | Person assigned to ticket |
| Priority | JIRA priority level |
| Created | Ticket creation date |
| Updated | Last update date |

### Custom Field Indicators

| Field | Description |
|-------|-------------|
| Has_Component | Indicates if standard component field might have data (127 tickets total) |
| Has_Company_Data | Indicates if cf[10413] might have company data |
| Has_Urgency_Data | Indicates if cf[10450] might have urgency data (TRI-1858 = High) |
| Has_Impact_Data | Indicates if cf[10451] might have impact data |

### Derived Business Fields

| Field | Description |
|-------|-------------|
| Client_CID | Client ID extracted from summary (e.g., CID 1769) |
| Category_From_Summary | Business category based on summary analysis |
| Issue_Category | Type of request (New, Change, Issue, Removal) |
| Contains_Emergency_Keywords | Yes/No for urgent language detection |

### Reference Fields

| Field | Description |
|-------|-------------|
| JIRA_URL | Direct link to ticket |
| Export_Date | Date when export was created |
| Is_TRI_1858 | Validation field for reference ticket |
| Known_Urgency_High | Validation for known urgency value |

