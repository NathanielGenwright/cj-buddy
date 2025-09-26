# MCP MySQL Server Usage Guide

This guide explains how to use the MCP (Model Context Protocol) server to query and analyze your Muni billing database with Claude.

## Quick Start

Once your MCP server is configured and running, you can immediately start asking Claude questions about your database in natural language.

### Example: Finding Customers by City

**You ask:** "How many customers are there in the city of Arcadia?"

**Claude responds:** "There are 3,800 customers in the city of Arcadia!"

Behind the scenes, Claude:
1. Connected to your MCP MySQL server
2. Explored the database structure
3. Found the `customers` table with a `city` column
4. Executed: `SELECT COUNT(*) FROM customers WHERE city LIKE '%Arcadia%'`
5. Returned the result in natural language

## Available MCP Tools

Your MCP server provides these tools that Claude can use:

### 1. `query` - Execute SQL Queries
Execute read-only SQL queries against your database.

**Example usage:**
- "Show me the most recent 10 bills"
- "What's the total outstanding balance?"
- "Find customers with automatic payments enabled"

### 2. `describe_table` - Table Structure Analysis
Get detailed information about any table's structure.

**Example usage:**
- "What's the structure of the customers table?"
- "Show me the columns in the bills table"
- "Describe the payments table schema"

### 3. `show_tables` - List All Tables
Display all available tables in the database.

**Example usage:**
- "What tables are available in the database?"
- "List all customer-related tables"
- "Show me the database structure"

### 4. `table_relationships` - Foreign Key Analysis
Explore relationships between tables.

**Example usage:**
- "How are customers linked to their bills?"
- "Show me the foreign key relationships"
- "What tables are connected to payments?"

## Common Query Patterns

### Customer Analysis

#### Count Customers by City
**Ask:** "How many customers are in each city?"

**Result:** Claude will show you customer counts by city, sorted by highest count.

#### Find Customer Details
**Ask:** "Show me details for customers in Redmond"

**Result:** Customer information including names, addresses, and account status.

#### Outstanding Balances
**Ask:** "Which customers have the highest outstanding balances?"

**Result:** List of customers with their balance amounts.

### Billing Analysis

#### Recent Bills
**Ask:** "Show me the most recent billing records"

**Result:** Latest bills with amounts, dates, and customer information.

#### Payment Patterns
**Ask:** "What's the average bill amount by month?"

**Result:** Monthly billing statistics and trends.

#### Automatic Payments
**Ask:** "How many customers use automatic payments?"

**Result:** Count and percentage of customers with auto-pay enabled.

### Database Exploration

#### Table Discovery
**Ask:** "What customer-related tables exist?"

**Result:** List of all tables containing customer data.

#### Schema Analysis
**Ask:** "What columns are in the customers table?"

**Result:** Complete column list with data types and descriptions.

#### Data Relationships
**Ask:** "How are bills connected to customers?"

**Result:** Explanation of foreign key relationships and table connections.

## Advanced Query Examples

### Complex Business Questions

#### Revenue Analysis
**Ask:** "What's the total revenue for the last 6 months by city?"

Claude will:
1. Find the appropriate billing/payment tables
2. Join with customer data for city information
3. Filter by date ranges
4. Calculate totals by city
5. Present results in an organized format

#### Customer Segmentation
**Ask:** "Show me customers who have been late on payments more than 3 times"

Claude will:
1. Analyze payment history tables
2. Calculate late payment counts per customer
3. Filter by the threshold
4. Present customer details

#### Operational Insights
**Ask:** "Which meters need reading this week?"

Claude will:
1. Find meter-related tables
2. Check reading schedules and dates
3. Identify overdue readings
4. Present actionable lists

## Working with Large Datasets

### Sampling Data
**Ask:** "Show me a sample of 10 customers from each city"

Claude will automatically limit results to prevent overwhelming output.

### Aggregated Views
**Ask:** "Give me summary statistics for customer balances"

Claude will provide:
- Total customers
- Average balance
- Min/max balances
- Distribution information

### Performance Considerations
The MCP server includes:
- **Query timeouts** (30 seconds max)
- **Connection limits** (10 concurrent)
- **Result size limits** to prevent memory issues
- **Query complexity validation**

## Data Security & Privacy

### Read-Only Access
- All queries are **read-only** - no data can be modified
- Database writes are completely blocked
- Original data remains unchanged

### Query Validation
- SQL injection prevention
- Dangerous operations blocked
- Query complexity limits enforced

### Audit Trail
- All queries are logged
- Connection attempts monitored
- Performance metrics tracked

## Troubleshooting Common Issues

### "No Results Found"
**Problem:** Query returns empty results
**Solution:** 
- Check spelling of city names, customer names, etc.
- Ask Claude to show sample data first
- Verify table structure with `describe_table`

**Example:**
```
You: "Show customers in Arkadia"
Claude: "No results found"

You: "Show me sample city names from the database"
Claude: "Cities include: Arcadia, Redmond, Dover..."

You: "Show customers in Arcadia" 
Claude: "Found 3,800 customers in Arcadia"
```

### "Connection Timeout"
**Problem:** Queries taking too long
**Solution:**
- Add LIMIT clauses to large queries
- Use aggregate functions instead of selecting all rows
- Ask for summaries rather than detailed lists

### "Table Not Found"
**Problem:** Referenced table doesn't exist
**Solution:**
- Ask Claude to list available tables first
- Use `show_tables` to explore the database
- Check table name spelling

## Advanced Usage Patterns

### Multi-Step Analysis

**Step 1:** "What customer tables are available?"
**Step 2:** "Show me the structure of the customers table"
**Step 3:** "How many customers are in the top 10 cities?"
**Step 4:** "Show me payment patterns for Arcadia customers"

### Comparative Analysis

**Ask:** "Compare customer counts between Arcadia and Redmond"

Claude will:
1. Query both cities
2. Present side-by-side comparison
3. Calculate differences and percentages
4. Provide insights

### Time-Series Analysis

**Ask:** "Show me billing trends over the past year"

Claude will:
1. Find relevant date columns
2. Group by time periods
3. Calculate totals and averages
4. Identify trends and patterns

## Integration with Business Processes

### Daily Operations
- "Which customers have overdue payments?"
- "What's today's expected revenue?"
- "List new customers from this week"

### Monthly Reporting  
- "Generate monthly customer growth report"
- "Show payment collection statistics"
- "Analyze service call patterns"

### Strategic Analysis
- "Identify high-value customer segments"
- "Analyze churn risk factors"
- "Evaluate service area profitability"

## Best Practices

### Effective Questioning
✅ **Good:** "How many customers are in Arcadia?"
❌ **Poor:** "Give me everything about customers"

✅ **Good:** "Show me recent bills with amounts over $500"
❌ **Poor:** "Show me all bills ever"

### Iterative Exploration
1. Start with broad questions
2. Drill down into specifics
3. Ask follow-up questions
4. Build on previous results

### Performance Optimization
- Use specific date ranges
- Limit result sets when exploring
- Ask for summaries of large datasets
- Use aggregate functions for statistics

## Getting Help

### Built-in Assistance
Claude can help you:
- Understand database structure
- Formulate better queries
- Interpret results
- Suggest related analysis

**Ask:** "Help me understand the database structure"
**Ask:** "What analysis would be useful for customer retention?"
**Ask:** "How should I interpret these billing patterns?"

### Documentation References
- MCP Server logs: `./scripts/mcp-logs.sh`
- Server status: `./scripts/mcp-status.sh`
- Configuration: `/mcp-servers/mysql-readonly/.env`

## Sample Session Transcript

```
User: Tell me about the customers in our database

Claude: I'll explore the customer data for you. Let me check the database structure first.

[Queries database structure]

I found a customers table with 390 total tables in your database. The customers table contains comprehensive information including:
- Basic info: names, addresses, contact details
- Account info: balances, due dates, account numbers  
- Billing preferences: email/mail delivery, automatic payments
- Service details: meter readings, shut-off dates, notes

What specific aspect of the customer data would you like to explore?

User: How many customers are there in the city of Arcadia?

Claude: [Queries: SELECT COUNT(*) FROM customers WHERE city LIKE '%Arcadia%']

There are 3,800 customers in the city of Arcadia!

I can also see that your database contains customers from many cities, with Clarksville having the most customers (639K+), followed by Redmond (23K+) and others.

User: What's the average balance for Arcadia customers?

Claude: [Queries: SELECT AVG(balance_current) FROM customers WHERE city LIKE '%Arcadia%']

The average current balance for customers in Arcadia is $127.45.

Some additional insights:
- Total outstanding balance for Arcadia: $484,300
- Customers with zero balance: 2,847 (75%)  
- Customers with balances over $500: 23 (0.6%)

Would you like me to analyze any other aspects of the Arcadia customer base?
```

## Next Steps

Once you're comfortable with basic queries, you can:

1. **Explore Complex Relationships** - Analyze how different data points connect
2. **Build Custom Reports** - Create recurring analysis patterns
3. **Monitor Key Metrics** - Track important business indicators
4. **Identify Trends** - Discover patterns in your data
5. **Support Decision Making** - Use insights for business strategy

The MCP server gives you powerful, safe access to your billing database through natural language conversation with Claude!