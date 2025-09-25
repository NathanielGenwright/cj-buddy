# Muni MCP MySQL Server

A Model Context Protocol (MCP) server that provides read-only access to the Muni project's MySQL databases, enabling AI assistants like Claude to safely query database schemas and data.

## Quick Start

1. **Setup Environment**
   ```bash
   cd mcp-servers/mysql-readonly
   cp .env.example .env
   # Edit .env with your database credentials
   npm install
   ```

2. **Test Connection**
   ```bash
   npm run test
   ```

3. **Start Server**
   ```bash
   # Using helper script (recommended)
   ./scripts/mcp-start.sh
   
   # Or directly with npm
   npm start
   ```

4. **Configure Claude**
   - Follow instructions in `claude-mcp-setup.md`
   - Add server configuration to Claude Desktop or Claude Code

## What This Provides

### 🔍 Database Exploration
- View all tables and their structures
- Understand relationships between tables
- Explore data patterns and sample records

### 🛡️ Safe Querying
- Read-only access prevents data modification
- Query validation and timeout protection
- SQL injection prevention

### 🤖 AI Integration
- Works with Claude Desktop and Claude Code
- Structured responses for database queries
- Natural language database interaction

## Available Tools & Usage Examples

Once connected, you can ask Claude:

### 🔍 Database Structure Questions
- **"What tables are available in the database?"**
- **"Show me customer-related tables"**
- **"What's the structure of the customers table?"**
- **"How are bills connected to customers?"**

### 📊 Business Intelligence Queries
- **"How many customers are there in the city of Arcadia?"**
  *Result: 3,800 customers*
- **"What's the total outstanding balance across all customers?"**
- **"Which customers use automatic payments?"**
- **"Show me recent billing activity"**

### 📈 Data Analysis Questions
- **"What's the average bill amount by city?"**
- **"Find customers with the highest balances"**
- **"Show payment trends over the last 6 months"**
- **"Which cities have the most customers?"**

### 🔧 Operational Insights  
- **"Which customers have overdue payments?"**
- **"Find customers who haven't paid in 60 days"**
- **"Show customers with shut-off notices"**
- **"List new customers from this month"**

## Project Structure

```
mcp-servers/mysql-readonly/
├── server.js              # Main MCP server implementation
├── test-connection.js     # Database connection testing
├── package.json           # Node.js dependencies
├── config.json           # Server configuration
├── .env.example          # Environment template
├── claude-config.json    # Claude Desktop configuration
└── logs/                 # Server logs
```

## Management Scripts

Located in `scripts/`:

- **`mcp-start.sh`** - Start the MCP server
- **`mcp-stop.sh`** - Stop the MCP server
- **`mcp-status.sh`** - Check server status
- **`mcp-logs.sh`** - View server logs

Examples:
```bash
./scripts/mcp-start.sh --dev      # Start with development database
./scripts/mcp-start.sh --test     # Start with test database
./scripts/mcp-status.sh --verbose # Detailed status information
./scripts/mcp-logs.sh --tail 100  # View last 100 log lines
```

## Docker Support

### Using Docker Compose

```bash
# Start as part of the main stack
docker-compose -f docker-compose.yml -f docker-compose.mcp.yml up -d

# Or start just the MCP service
docker-compose -f docker-compose.mcp.yml up -d mcp-mysql-server
```

### Standalone Docker

```bash
cd mcp-servers/mysql-readonly
docker build -t muni-mcp-mysql .
docker run -d --name mcp-server \
  --env-file .env \
  --network muni_default \
  -p 3333:3333 \
  muni-mcp-mysql
```

## Configuration

### Environment Variables

Key settings in `.env`:

```bash
# Database connections
MYSQL_DEV_HOST=localhost
MYSQL_DEV_PORT=3307
MYSQL_DEV_DATABASE=your_database
MYSQL_DEV_USER=your_user
MYSQL_DEV_PASSWORD=your_password

# Security settings
MCP_READ_ONLY=true
MCP_QUERY_TIMEOUT=30000
MCP_MAX_QUERY_LENGTH=10000
```

### Security Features

- **Read-only access**: Only SELECT, SHOW, DESCRIBE operations allowed
- **Query validation**: Prevents dangerous SQL patterns
- **Connection limits**: Prevents resource exhaustion
- **Timeout protection**: Prevents long-running queries
- **Audit logging**: All queries are logged for review

## Troubleshooting

### Common Issues

1. **Connection refused**
   ```bash
   # Check if Docker databases are running
   docker-compose ps | grep bdb-
   
   # Test connection manually
   cd mcp-servers/mysql-readonly && npm run test
   ```

2. **MCP not appearing in Claude**
   - Verify file paths in Claude configuration
   - Check that Node.js is accessible to Claude
   - Restart Claude Desktop after configuration changes
   - Run: `claude mcp list` to verify server is configured

3. **Query returns no results**
   - Check spelling (e.g., "Arcadia" not "Arkadia")
   - Ask Claude to show sample data first
   - Use broader search terms initially

4. **Permission errors**
   ```bash
   # Make scripts executable
   chmod +x scripts/mcp-*.sh
   
   # Check database user permissions
   ./scripts/mcp-status.sh --verbose
   ```

### Debug Mode

Enable verbose logging:
```bash
export MCP_ENABLE_LOGGING=true
export MCP_LOG_QUERIES=true
./scripts/mcp-start.sh --dev
```

## Database Schema Overview

The Muni system contains several key areas:

### Core Tables
- **customers** - Customer account information
- **bills** - Billing records and statements  
- **payments** - Payment transactions
- **meters** - Utility meters and readings
- **accounts** - Account balances and adjustments

### Supporting Tables
- **companies** - Utility company configurations
- **rates** - Billing rate structures
- **service_calls** - Maintenance and service records
- **parcels** - Property/parcel information

### Sample Queries

Try these with Claude once connected:

```sql
-- Show all customer-related tables
SHOW TABLES LIKE '%customer%';

-- Get recent billing records
SELECT * FROM bills ORDER BY created_at DESC LIMIT 10;

-- Find tables with foreign key relationships
SELECT 
  TABLE_NAME,
  COLUMN_NAME,
  REFERENCED_TABLE_NAME,
  REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE REFERENCED_TABLE_NAME IS NOT NULL;
```

## Development

### Adding New Features

1. **Server modifications**: Edit `server.js`
2. **Test changes**: `npm run test`
3. **Update documentation**: Update relevant `.md` files
4. **Test with Claude**: Verify MCP integration works

### Contributing

1. Follow existing code style and patterns
2. Add tests for new functionality
3. Update documentation
4. Test with both development and test databases

## Security Considerations

### Database Access
- Use dedicated read-only MySQL user
- Limit permissions to SELECT operations only
- Enable SSL/TLS for connections
- Regularly rotate database credentials

### Network Security
- Run MCP server in isolated Docker network
- Use firewall rules to limit access
- Monitor connection attempts and query patterns

### Query Security
- All queries validated before execution
- Dangerous SQL patterns are blocked
- Query length and complexity limits enforced
- Comprehensive audit logging enabled

## Real-World Usage Example

**Question**: "How many customers are there in the city of Arcadia?"

**Claude's Response**: "There are 3,800 customers in the city of Arcadia!"

**Behind the scenes**, Claude:
1. Connected to your MCP MySQL server
2. Explored the database structure 
3. Found the `customers` table with a `city` column
4. Executed: `SELECT COUNT(*) FROM customers WHERE city LIKE '%Arcadia%'`
5. Returned the result in natural language

This demonstrates the power of natural language database queries through the MCP server!

## Documentation & Support

- **Quick Start**: This README
- **Detailed Setup**: `docs/mcp-setup.md`
- **Usage Examples**: `docs/mcp-usage-guide.md`
- **Claude Integration**: `claude-mcp-setup.md`
- **Troubleshooting**: Check logs with `./scripts/mcp-logs.sh`
- **Issues**: Report problems in the main project repository

## Getting Started

1. **Setup**: Follow `docs/mcp-setup.md`
2. **Configure**: Use `claude-mcp-setup.md` for Claude integration
3. **Test**: Ask "How many tables are in the database?"
4. **Explore**: Try the usage examples above
5. **Analyze**: Start asking business questions about your data

---

**Security Note**: This MCP server provides read-only access to protect production data. All queries are validated and logged for security.