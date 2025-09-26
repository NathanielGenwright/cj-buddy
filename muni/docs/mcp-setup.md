# MCP MySQL Database Server Setup Guide

## Overview

This guide explains how to set up a Model Context Protocol (MCP) server for read-only access to the Muni project's MySQL databases. This enables Claude and other AI assistants to query database schemas and data safely through a standardized protocol.

## What is MCP?

Model Context Protocol (MCP) is an open-source standard that enables AI assistants to securely connect to external data sources, tools, and APIs. In our case, it allows Claude to:

- Inspect database schemas and table structures
- Execute read-only SQL queries
- Analyze data patterns and relationships
- Generate insights from database content
- Assist with database-related development tasks

## Architecture

```
Claude Desktop/Code ↔ MCP Server ↔ Docker MySQL Containers
```

The MCP server acts as a secure intermediary between Claude and the MySQL databases running in Docker containers.

## Prerequisites

1. **Node.js** (version 18 or higher)
2. **npm** or **pnpm** package manager
3. **Docker** and **Docker Compose** (for database containers)
4. **Claude Desktop** or **Claude Code** (for AI assistant access)

## Database Connection Details

The Muni project uses the following MySQL database configurations:

### Development Database
- **Container**: `bdb-dev`
- **Host**: `localhost` (when connecting from host machine)
- **Port**: `3307` (configurable via `BDBDEV_PORT`)
- **Database**: Configured via `BDBDEV_NAME`
- **User**: Configured via `BDBDEV_USER`
- **Password**: Configured via `BDBDEV_PASS`

### Test Database
- **Container**: `bdb-test`
- **Host**: `localhost`
- **Port**: `3308` (configurable via `BDBTEST_PORT`)
- **Database**: `billingdbtest` (default) or configured via `BDBTEST_NAME`
- **User**: Configured via `BDBTEST_USER`
- **Password**: Configured via `BDBTEST_PASS`

## Installation Steps

### Step 1: Install MCP MySQL Server

```bash
# Global installation (recommended)
npm install -g @benborla29/mcp-server-mysql

# Or install locally in project
cd /path/to/muni
npm install @benborla29/mcp-server-mysql
```

### Step 2: Create MCP Configuration Directory

```bash
mkdir -p mcp-servers/mysql-readonly
cd mcp-servers/mysql-readonly
```

### Step 3: Environment Configuration

Create a `.env` file with database connection details:

```bash
# .env file for MCP MySQL Server

# Development Database
MYSQL_DEV_HOST=localhost
MYSQL_DEV_PORT=3307
MYSQL_DEV_DATABASE=your_dev_database_name
MYSQL_DEV_USER=your_dev_user
MYSQL_DEV_PASSWORD=your_dev_password

# Test Database
MYSQL_TEST_HOST=localhost
MYSQL_TEST_PORT=3308
MYSQL_TEST_DATABASE=billingdbtest
MYSQL_TEST_USER=your_test_user
MYSQL_TEST_PASSWORD=your_test_password

# MCP Server Configuration
MCP_SERVER_PORT=3333
MCP_MAX_CONNECTIONS=10
MCP_QUERY_TIMEOUT=30000
MCP_READ_ONLY=true
MCP_SSL_MODE=preferred

# Security Settings
MCP_ALLOWED_SCHEMAS=*
MCP_MAX_QUERY_LENGTH=10000
MCP_ENABLE_LOGGING=true
```

### Step 4: Create Server Configuration

Create a `config.json` file:

```json
{
  "server": {
    "name": "muni-mysql-readonly",
    "version": "1.0.0",
    "port": 3333,
    "host": "localhost"
  },
  "databases": {
    "development": {
      "host": "${MYSQL_DEV_HOST}",
      "port": "${MYSQL_DEV_PORT}",
      "database": "${MYSQL_DEV_DATABASE}",
      "user": "${MYSQL_DEV_USER}",
      "password": "${MYSQL_DEV_PASSWORD}",
      "ssl": {
        "mode": "preferred"
      }
    },
    "test": {
      "host": "${MYSQL_TEST_HOST}",
      "port": "${MYSQL_TEST_PORT}",
      "database": "${MYSQL_TEST_DATABASE}",
      "user": "${MYSQL_TEST_USER}",
      "password": "${MYSQL_TEST_PASSWORD}",
      "ssl": {
        "mode": "preferred"
      }
    }
  },
  "security": {
    "readOnly": true,
    "maxConnections": 10,
    "queryTimeout": 30000,
    "maxQueryLength": 10000,
    "allowedOperations": ["SELECT", "SHOW", "DESCRIBE", "EXPLAIN"]
  },
  "logging": {
    "enabled": true,
    "level": "info",
    "logQueries": true
  }
}
```

### Step 5: Create Package.json

```json
{
  "name": "muni-mcp-mysql-server",
  "version": "1.0.0",
  "description": "MCP MySQL server for Muni project database access",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "node test-connection.js"
  },
  "dependencies": {
    "@benborla29/mcp-server-mysql": "latest",
    "dotenv": "^16.3.1",
    "mysql2": "^3.6.5"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  },
  "keywords": ["mcp", "mysql", "database", "ai", "claude"],
  "author": "Muni Development Team",
  "license": "MIT"
}
```

### Step 6: Create Server Launcher

Create a `server.js` file:

```javascript
#!/usr/bin/env node

const { MCPServer } = require('@benborla29/mcp-server-mysql');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

// Configuration
const config = {
  // Development database connection
  development: {
    host: process.env.MYSQL_DEV_HOST || 'localhost',
    port: parseInt(process.env.MYSQL_DEV_PORT) || 3307,
    database: process.env.MYSQL_DEV_DATABASE,
    user: process.env.MYSQL_DEV_USER,
    password: process.env.MYSQL_DEV_PASSWORD,
    ssl: {
      mode: process.env.MCP_SSL_MODE || 'preferred'
    }
  },
  
  // Test database connection
  test: {
    host: process.env.MYSQL_TEST_HOST || 'localhost',
    port: parseInt(process.env.MYSQL_TEST_PORT) || 3308,
    database: process.env.MYSQL_TEST_DATABASE || 'billingdbtest',
    user: process.env.MYSQL_TEST_USER,
    password: process.env.MYSQL_TEST_PASSWORD,
    ssl: {
      mode: process.env.MCP_SSL_MODE || 'preferred'
    }
  }
};

// Server options
const serverOptions = {
  readOnly: process.env.MCP_READ_ONLY !== 'false',
  maxConnections: parseInt(process.env.MCP_MAX_CONNECTIONS) || 10,
  queryTimeout: parseInt(process.env.MCP_QUERY_TIMEOUT) || 30000,
  maxQueryLength: parseInt(process.env.MCP_MAX_QUERY_LENGTH) || 10000,
  enableLogging: process.env.MCP_ENABLE_LOGGING === 'true'
};

// Create and start MCP server
async function startServer() {
  try {
    console.log('🚀 Starting Muni MCP MySQL Server...');
    
    // Determine which database to connect to
    const dbConfig = process.argv.includes('--test') ? config.test : config.development;
    const dbName = process.argv.includes('--test') ? 'test' : 'development';
    
    console.log(`📦 Connecting to ${dbName} database at ${dbConfig.host}:${dbConfig.port}`);
    
    const server = new MCPServer(dbConfig, serverOptions);
    
    // Handle graceful shutdown
    process.on('SIGINT', async () => {
      console.log('\n🛑 Shutting down MCP server...');
      await server.close();
      process.exit(0);
    });
    
    // Start the server
    await server.start();
    console.log(`✅ MCP MySQL Server running for ${dbName} database`);
    console.log('🔍 Ready to accept queries from Claude!');
    
  } catch (error) {
    console.error('❌ Failed to start MCP server:', error.message);
    process.exit(1);
  }
}

// Start the server
startServer();
```

## Claude Configuration

### For Claude Desktop

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "muni-mysql-dev": {
      "command": "node",
      "args": [
        "/path/to/muni/mcp-servers/mysql-readonly/server.js"
      ],
      "env": {
        "NODE_ENV": "development"
      }
    },
    "muni-mysql-test": {
      "command": "node",
      "args": [
        "/path/to/muni/mcp-servers/mysql-readonly/server.js",
        "--test"
      ],
      "env": {
        "NODE_ENV": "test"
      }
    }
  }
}
```

### For Claude Code

Use the Claude Code CLI:

```bash
# Add development database server
claude mcp add muni-mysql-dev --scope local -- \
  node /path/to/muni/mcp-servers/mysql-readonly/server.js

# Add test database server
claude mcp add muni-mysql-test --scope local -- \
  node /path/to/muni/mcp-servers/mysql-readonly/server.js --test
```

## Usage

### Starting the Docker Databases

First, ensure your MySQL containers are running:

```bash
# Start all services
docker-compose up -d

# Or start specific database services
docker-compose up -d bdb-dev bdb-test
```

### Testing the MCP Connection

Create a test script (`test-connection.js`):

```javascript
const mysql = require('mysql2/promise');
require('dotenv').config();

async function testConnection() {
  const configs = [
    {
      name: 'Development',
      host: process.env.MYSQL_DEV_HOST || 'localhost',
      port: parseInt(process.env.MYSQL_DEV_PORT) || 3307,
      user: process.env.MYSQL_DEV_USER,
      password: process.env.MYSQL_DEV_PASSWORD,
      database: process.env.MYSQL_DEV_DATABASE
    },
    {
      name: 'Test',
      host: process.env.MYSQL_TEST_HOST || 'localhost',
      port: parseInt(process.env.MYSQL_TEST_PORT) || 3308,
      user: process.env.MYSQL_TEST_USER,
      password: process.env.MYSQL_TEST_PASSWORD,
      database: process.env.MYSQL_TEST_DATABASE
    }
  ];

  for (const config of configs) {
    try {
      console.log(`Testing ${config.name} database connection...`);
      const connection = await mysql.createConnection(config);
      const [rows] = await connection.execute('SELECT VERSION() as version');
      console.log(`✅ ${config.name}: Connected to MySQL ${rows[0].version}`);
      await connection.end();
    } catch (error) {
      console.error(`❌ ${config.name}: Connection failed:`, error.message);
    }
  }
}

testConnection();
```

Run the test:

```bash
npm run test
```

### Sample Queries

Once connected through Claude, you can ask questions like:

- "Show me all tables in the database"
- "Describe the structure of the customers table"
- "What are the relationships between bills and payments?"
- "Show me the most recent 10 customer records"
- "Explain the billing workflow based on the database schema"

## Security Considerations

### Database User Permissions

Create a dedicated read-only MySQL user for MCP access:

```sql
-- Connect to MySQL as admin user
CREATE USER 'mcp_readonly'@'%' IDENTIFIED BY 'secure_password_here';

-- Grant SELECT permissions only
GRANT SELECT ON your_database.* TO 'mcp_readonly'@'%';

-- Grant schema inspection permissions
GRANT SHOW VIEW ON your_database.* TO 'mcp_readonly'@'%';

-- Flush privileges
FLUSH PRIVILEGES;
```

### Connection Security

- Use SSL/TLS encryption for database connections
- Store credentials in environment variables, not in code
- Implement query timeouts and connection limits
- Enable query logging for audit purposes
- Restrict allowed SQL operations to read-only queries

### Network Security

- Use Docker networks to isolate database access
- Consider running MCP server in a separate container
- Implement proper firewall rules
- Monitor connection attempts and query patterns

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Verify Docker containers are running: `docker ps`
   - Check port mappings and firewall settings
   - Confirm environment variables are set correctly: `npm run validate`

2. **Authentication Failed**
   - Verify database user credentials in `.env` file
   - Check user permissions in MySQL
   - Ensure SSL settings match database requirements

3. **MCP Server Not Starting**
   - Check Node.js version compatibility (18+ required)
   - Verify all npm packages are installed: `npm install`
   - Review server logs for error details: `./scripts/mcp-logs.sh`

4. **Claude Not Seeing MCP Server**
   - Restart Claude Desktop/Code after configuration changes
   - Verify file paths in configuration match your system
   - Check that Node.js is accessible to Claude: `which node`
   - Ensure MCP server is running: `./scripts/mcp-status.sh`

5. **Query Timeouts or Errors**
   - Check query complexity and add LIMIT clauses
   - Verify table and column names exist
   - Use aggregate functions for large datasets
   - Check server logs: `./scripts/mcp-logs.sh`

6. **No Results from Queries**
   - Verify data exists in the database
   - Check spelling of search terms (e.g., "Arcadia" vs "Arkadia")
   - Use LIKE '%term%' for partial matches
   - Ask Claude to show sample data first

### Debug Mode

Enable verbose logging by setting:

```bash
export MCP_ENABLE_LOGGING=true
export NODE_ENV=development
```

### Logs Location

Server logs are written to:
- Console output (when run manually)
- System logs (when run as service)
- `logs/mcp-server.log` (if configured)

## Advanced Configuration

### Multiple Database Support

You can configure the MCP server to connect to multiple databases:

```javascript
const configs = {
  billing: { /* billing database config */ },
  customer: { /* customer portal config */ },
  login: { /* login service config */ }
};
```

### Custom Query Limits

Adjust security settings in `config.json`:

```json
{
  "security": {
    "maxQueryLength": 5000,
    "queryTimeout": 15000,
    "allowedTables": ["customers", "bills", "payments"],
    "deniedTables": ["admin_users", "api_keys"]
  }
}
```

### Performance Tuning

For production use:

```json
{
  "performance": {
    "connectionPool": {
      "min": 2,
      "max": 10,
      "idle": 30000
    },
    "queryCache": {
      "enabled": true,
      "ttl": 300000
    }
  }
}
```

## Integration with Development Workflow

### Docker Compose Service

Add to your `docker-compose.yml`:

```yaml
services:
  mcp-mysql:
    build:
      context: ./mcp-servers/mysql-readonly
    environment:
      - MYSQL_DEV_HOST=bdb-dev
      - MYSQL_TEST_HOST=bdb-test
      # ... other env vars
    depends_on:
      - bdb-dev
      - bdb-test
    networks:
      - muni-network
```

### Helper Scripts

Create convenience scripts in `scripts/` directory:

- `mcp-start.sh` - Start MCP server
- `mcp-stop.sh` - Stop MCP server
- `mcp-restart.sh` - Restart MCP server
- `mcp-logs.sh` - View server logs
- `mcp-test.sh` - Test database connectivity

## Next Steps

After successful setup:

1. **Test Basic Connectivity**: Verify MCP server can connect to databases
2. **Configure Claude**: Add server to Claude Desktop or Claude Code
3. **Test Queries**: Try basic schema inspection and data queries
4. **Monitor Performance**: Watch for connection limits and query timeouts
5. **Implement Logging**: Set up proper log rotation and monitoring
6. **Security Audit**: Review permissions and access patterns
7. **Documentation**: Document common queries and use cases for your team

## Support

For issues specific to:
- **MCP Protocol**: Check [Model Context Protocol documentation](https://modelcontextprotocol.io/)
- **MySQL Server Package**: See [@benborla29/mcp-server-mysql](https://github.com/benborla/mcp-server-mysql)
- **Muni Project**: Consult the main project documentation or team leads

---

**Security Note**: Always use read-only database credentials and never expose production database credentials in development configurations.