# Claude MCP Setup Instructions

This file provides quick setup instructions for adding the Muni MySQL MCP server to Claude Desktop or Claude Code.

## Prerequisites

1. Ensure you have completed the MCP server setup according to `/docs/mcp-setup.md`
2. Verify your `.env` file is configured with correct database credentials
3. Test the connection using `npm run test` in the MCP server directory

## Claude Desktop Configuration

### Location of Configuration File

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

### Add to Existing Configuration

If you already have a `claude_desktop_config.json` file, add the following to the `mcpServers` section:

```json
{
  "mcpServers": {
    "muni-mysql-dev": {
      "command": "node",
      "args": [
        "/Users/munin8/_myprojects/muni/mcp-servers/mysql-readonly/server.js",
        "--dev"
      ],
      "env": {
        "NODE_ENV": "development"
      }
    },
    "muni-mysql-test": {
      "command": "node", 
      "args": [
        "/Users/munin8/_myprojects/muni/mcp-servers/mysql-readonly/server.js",
        "--test"
      ],
      "env": {
        "NODE_ENV": "test"
      }
    }
  }
}
```

### Create New Configuration

If you don't have a configuration file, create it with the complete structure:

```json
{
  "mcpServers": {
    "muni-mysql-dev": {
      "command": "node",
      "args": [
        "/Users/munin8/_myprojects/muni/mcp-servers/mysql-readonly/server.js",
        "--dev"
      ],
      "env": {
        "NODE_ENV": "development"
      }
    },
    "muni-mysql-test": {
      "command": "node", 
      "args": [
        "/Users/munin8/_myprojects/muni/mcp-servers/mysql-readonly/server.js",
        "--test"
      ],
      "env": {
        "NODE_ENV": "test"
      }
    }
  }
}
```

**Important**: Update the file paths to match your actual project location!

## Claude Code Configuration

Use the Claude Code CLI to add the MCP servers:

```bash
# Add development database server
claude mcp add muni-mysql-dev --scope local -- \
  node /Users/munin8/_myprojects/muni/mcp-servers/mysql-readonly/server.js --dev

# Add test database server  
claude mcp add muni-mysql-test --scope local -- \
  node /Users/munin8/_myprojects/muni/mcp-servers/mysql-readonly/server.js --test
```

### Alternative: Global Installation

If you prefer to install globally:

```bash
# Install the MCP server package globally
cd /Users/munin8/_myprojects/muni/mcp-servers/mysql-readonly
npm run install-mcp

# Then add to Claude Code with simpler commands
claude mcp add muni-mysql-dev --scope local -- \
  muni-mcp-mysql-server --dev

claude mcp add muni-mysql-test --scope local -- \
  muni-mcp-mysql-server --test
```

## Verification

### 1. Restart Claude Desktop
After updating the configuration, restart Claude Desktop completely.

### 2. Check for MCP Connection
In a new Claude conversation, you should see an MCP indicator or be able to use commands like:

- "Show me all tables in the database"
- "What's the structure of the customers table?"
- "Query the database for recent billing records"

### 3. Test Basic Functionality

Try these sample queries:

```
Can you show me all tables in the Muni development database?
```

```
What's the schema of the bills table?
```

```
Show me the relationships between customers and bills tables.
```

## Troubleshooting

### MCP Server Not Appearing in Claude

1. **Check file paths**: Ensure the paths in your configuration match your actual project location
2. **Verify Node.js**: Make sure Node.js is in your PATH and accessible to Claude
3. **Check permissions**: Ensure Claude has permission to execute the script
4. **Review logs**: Check Claude Desktop logs for MCP connection errors

### Database Connection Issues

1. **Test connection manually**:
   ```bash
   cd /Users/munin8/_myprojects/muni/mcp-servers/mysql-readonly
   npm run test
   ```

2. **Verify Docker containers are running**:
   ```bash
   docker-compose ps
   ```

3. **Check environment variables**: Ensure `.env` file has correct database credentials

### Permission Errors

1. **Make server.js executable**:
   ```bash
   chmod +x /Users/munin8/_myprojects/muni/mcp-servers/mysql-readonly/server.js
   ```

2. **Check Node.js installation**:
   ```bash
   which node
   node --version
   ```

## Advanced Configuration

### Custom Environment Variables

You can pass additional environment variables through Claude's configuration:

```json
{
  "mcpServers": {
    "muni-mysql-dev": {
      "command": "node",
      "args": [
        "/Users/munin8/_myprojects/muni/mcp-servers/mysql-readonly/server.js",
        "--dev"
      ],
      "env": {
        "NODE_ENV": "development",
        "MCP_LOG_QUERIES": "true",
        "MCP_QUERY_TIMEOUT": "60000"
      }
    }
  }
}
```

### Multiple Project Configurations

If you work with multiple Muni environments:

```json
{
  "mcpServers": {
    "muni-local-dev": {
      "command": "node",
      "args": [
        "/Users/munin8/_myprojects/muni/mcp-servers/mysql-readonly/server.js",
        "--dev"
      ],
      "env": {
        "NODE_ENV": "development"
      }
    },
    "muni-staging": {
      "command": "node",
      "args": [
        "/Users/munin8/_myprojects/muni-staging/mcp-servers/mysql-readonly/server.js",
        "--dev"
      ],
      "env": {
        "NODE_ENV": "staging"
      }
    }
  }
}
```

## Security Considerations

1. **Read-only access**: The MCP server is configured for read-only access by default
2. **Query validation**: All queries are validated before execution
3. **Connection limits**: Connection pooling prevents resource exhaustion
4. **Credential security**: Database credentials are stored in `.env` files, not in configuration

## Testing Your Connection

After setup, test the MCP connection:

1. **Ask Claude a simple question:**
   ```
   "How many tables are in the database?"
   ```

2. **Try a specific query:**
   ```
   "Show me the structure of the customers table"
   ```

3. **Test with real data:**
   ```
   "How many customers are there in the city of Arcadia?"
   ```
   *Expected result: Should return the actual count (e.g., 3,800)*

## Usage Examples

Once connected, you can ask Claude:

### Database Structure Questions
- "What tables are available in the database?"
- "Show me customer-related tables"
- "What's the structure of the bills table?"
- "How are customers linked to their payments?"

### Business Intelligence Questions  
- "How many customers are in each city?"
- "What's the total outstanding balance?"
- "Which customers use automatic payments?"
- "Show me recent billing activity"

### Data Analysis Questions
- "What's the average bill amount by city?"
- "Find customers with the highest balances"
- "Show payment trends over time"
- "Analyze customer demographics"

## Available MCP Tools

Your MCP server provides these tools:

1. **`query`** - Execute read-only SQL queries
2. **`describe_table`** - Get table structure details  
3. **`show_tables`** - List all database tables
4. **`table_relationships`** - Show foreign key relationships

## Performance & Limits

- **Query timeout:** 30 seconds maximum
- **Connection limit:** 10 concurrent connections
- **Read-only access:** No data modification possible
- **Query validation:** SQL injection prevention enabled

## Troubleshooting

### Connection Issues
```bash
# Check if MCP server is running
./scripts/mcp-status.sh

# View server logs
./scripts/mcp-logs.sh

# Test database connection
npm run test
```

### Claude Not Responding
1. Restart Claude Desktop/Code after configuration changes
2. Verify file paths in configuration match your system
3. Check that Node.js is accessible to Claude
4. Ensure MCP server is running

### Query Issues
- Start with simple questions like table counts
- Use `show_tables` to explore available data
- Ask Claude to describe table structures first
- Check spelling of table/column names

## Next Steps

After successful setup:

1. **Explore Your Data** - Start with the usage examples above
2. **Analyze Business Patterns** - Ask specific questions about your operations
3. **Generate Reports** - Use Claude to create regular business intelligence
4. **Monitor Key Metrics** - Track important business indicators
5. **Support Decisions** - Leverage insights for strategic planning

## Advanced Usage

For more detailed usage instructions and advanced examples, see:
- **Usage Guide:** `/docs/mcp-usage-guide.md`
- **README:** `/README-MCP.md`
- **Setup Guide:** `/docs/mcp-setup.md`

---

**Note**: Remember to update file paths in the configuration to match your actual project location!