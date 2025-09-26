#!/usr/bin/env node

/**
 * Muni MCP MySQL Server
 * 
 * A Model Context Protocol server for read-only access to Muni project MySQL databases.
 * This server enables Claude and other AI assistants to safely query database schemas
 * and data through a standardized protocol.
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { CallToolRequestSchema, ListResourcesRequestSchema, ListToolsRequestSchema, ReadResourceRequestSchema } = require('@modelcontextprotocol/sdk/types.js');
const mysql = require('mysql2/promise');
const path = require('path');
const fs = require('fs');
require('dotenv').config({ path: path.join(__dirname, '.env') });

class MuniMySQLServer {
  constructor() {
    this.server = new Server({
      name: 'muni-mysql-readonly',
      version: '1.0.0'
    }, {
      capabilities: {
        resources: {},
        tools: {}
      }
    });
    
    this.pool = null;
    this.config = this.loadConfig();
    this.setupHandlers();
  }

  loadConfig() {
    // Determine which database to connect to based on command line arguments
    const isTestMode = process.argv.includes('--test');
    const isDevelopment = process.argv.includes('--dev') || !isTestMode;
    
    const dbMode = isTestMode ? 'test' : 'development';
    
    console.error(`🔧 Starting in ${dbMode} mode`);
    
    // Map database mode to environment variable prefixes
    const envPrefix = isTestMode ? 'MYSQL_TEST' : 'MYSQL_DEV';
    
    const config = {
      mode: dbMode,
      database: {
        host: process.env[`${envPrefix}_HOST`] || 'localhost',
        port: parseInt(process.env[`${envPrefix}_PORT`]) || (isTestMode ? 3308 : 3307),
        database: process.env[`${envPrefix}_DATABASE`] || (isTestMode ? 'billingdbtest' : undefined),
        user: process.env[`${envPrefix}_USER`],
        password: process.env[`${envPrefix}_PASSWORD`],
        charset: 'latin1',
        timezone: 'UTC',
        // SSL disabled for Cloud SQL proxy connection
        ssl: false,
        acquireTimeout: 60000,
        connectionLimit: parseInt(process.env.MCP_MAX_CONNECTIONS) || 10,
        queueLimit: 0,
        reconnect: true,
        multipleStatements: false
      },
      security: {
        readOnly: process.env.MCP_READ_ONLY !== 'false',
        queryTimeout: parseInt(process.env.MCP_QUERY_TIMEOUT) || 30000,
        maxQueryLength: parseInt(process.env.MCP_MAX_QUERY_LENGTH) || 10000,
        allowedOperations: ['SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN', 'DESC'],
        logQueries: process.env.MCP_LOG_QUERIES === 'true'
      }
    };

    // Validate required configuration
    if (!config.database.user || !config.database.password) {
      throw new Error(`Missing required database credentials for ${dbMode} mode. Check your .env file.`);
    }

    return config;
  }

  async createConnection() {
    try {
      this.pool = mysql.createPool(this.config.database);
      
      // Test the connection
      const connection = await this.pool.getConnection();
      const [rows] = await connection.execute('SELECT VERSION() as version, DATABASE() as current_database');
      connection.release();
      
      console.error(`✅ Connected to MySQL ${rows[0].version} - Database: ${rows[0].current_database || 'None selected'}`);
      return true;
    } catch (error) {
      console.error(`❌ Database connection failed:`, error.message);
      throw error;
    }
  }

  setupHandlers() {
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
      resources: [
        {
          uri: 'mysql://schema',
          name: 'Database Schema',
          description: 'Complete database schema including tables, columns, and relationships',
          mimeType: 'application/json'
        },
        {
          uri: 'mysql://tables',
          name: 'Database Tables',
          description: 'List of all tables in the database',
          mimeType: 'application/json'
        }
      ]
    }));

    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;
      
      try {
        if (uri === 'mysql://schema') {
          return {
            contents: [{
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(await this.getCompleteSchema(), null, 2)
            }]
          };
        } else if (uri === 'mysql://tables') {
          return {
            contents: [{
              uri,
              mimeType: 'application/json',
              text: JSON.stringify(await this.getTables(), null, 2)
            }]
          };
        }
        
        throw new Error(`Unknown resource: ${uri}`);
      } catch (error) {
        throw new Error(`Failed to read resource ${uri}: ${error.message}`);
      }
    });

    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'query',
          description: 'Execute a read-only SQL query against the database',
          inputSchema: {
            type: 'object',
            properties: {
              sql: {
                type: 'string',
                description: 'SQL query to execute (SELECT, SHOW, DESCRIBE, EXPLAIN only)'
              }
            },
            required: ['sql']
          }
        },
        {
          name: 'describe_table',
          description: 'Get detailed information about a table structure',
          inputSchema: {
            type: 'object',
            properties: {
              table: {
                type: 'string',
                description: 'Name of the table to describe'
              }
            },
            required: ['table']
          }
        },
        {
          name: 'show_tables',
          description: 'List all tables in the database',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        },
        {
          name: 'table_relationships',
          description: 'Show foreign key relationships for the database',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        }
      ]
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        switch (name) {
          case 'query':
            return await this.executeQuery(args.sql);
          case 'describe_table':
            return await this.describeTable(args.table);
          case 'show_tables':
            return await this.showTables();
          case 'table_relationships':
            return await this.getTableRelationships();
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`
            }
          ]
        };
      }
    });
  }

  validateQuery(sql) {
    const trimmed = sql.trim().toUpperCase();
    const allowedOperations = this.config.security.allowedOperations;
    
    // Check if query starts with allowed operation
    const isAllowed = allowedOperations.some(op => trimmed.startsWith(op));
    
    if (!isAllowed) {
      throw new Error(`Query not allowed. Only ${allowedOperations.join(', ')} operations are permitted.`);
    }
    
    // Check query length
    if (sql.length > this.config.security.maxQueryLength) {
      throw new Error(`Query too long. Maximum length is ${this.config.security.maxQueryLength} characters.`);
    }
    
    // Basic SQL injection prevention
    const dangerousPatterns = [
      /;\s*(drop|delete|update|insert|create|alter|truncate)/i,
      /union\s+select/i,
      /--/,
      /\/\*/
    ];
    
    for (const pattern of dangerousPatterns) {
      if (pattern.test(sql)) {
        throw new Error('Query contains potentially dangerous patterns.');
      }
    }
    
    return true;
  }

  async executeQuery(sql) {
    this.validateQuery(sql);
    
    if (this.config.security.logQueries) {
      console.error(`📝 Executing query: ${sql.substring(0, 100)}${sql.length > 100 ? '...' : ''}`);
    }
    
    try {
      const [rows, fields] = await this.pool.execute(sql);
      
      return {
        content: [
          {
            type: 'text',
            text: `Query executed successfully. ${Array.isArray(rows) ? rows.length : 0} rows returned.\n\n` +
                  `Results:\n${JSON.stringify(rows, null, 2)}`
          }
        ]
      };
    } catch (error) {
      throw new Error(`Query execution failed: ${error.message}`);
    }
  }

  async describeTable(tableName) {
    if (!tableName || typeof tableName !== 'string') {
      throw new Error('Table name is required');
    }
    
    // Sanitize table name (basic validation)
    if (!/^[a-zA-Z0-9_]+$/.test(tableName)) {
      throw new Error('Invalid table name. Only alphanumeric characters and underscores are allowed.');
    }
    
    try {
      const [structure] = await this.pool.execute(`DESCRIBE ${tableName}`);
      const [indexes] = await this.pool.execute(`SHOW INDEX FROM ${tableName}`);
      
      return {
        content: [
          {
            type: 'text',
            text: `Table: ${tableName}\n\n` +
                  `Structure:\n${JSON.stringify(structure, null, 2)}\n\n` +
                  `Indexes:\n${JSON.stringify(indexes, null, 2)}`
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to describe table ${tableName}: ${error.message}`);
    }
  }

  async showTables() {
    try {
      const [tables] = await this.pool.execute('SHOW TABLES');
      
      return {
        content: [
          {
            type: 'text',
            text: `Database Tables:\n${JSON.stringify(tables, null, 2)}`
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to show tables: ${error.message}`);
    }
  }

  async getTables() {
    try {
      const [tables] = await this.pool.execute('SHOW TABLES');
      return tables;
    } catch (error) {
      throw new Error(`Failed to get tables: ${error.message}`);
    }
  }

  async getCompleteSchema() {
    try {
      const [tables] = await this.pool.execute('SHOW TABLES');
      const schema = {
        database: this.config.database.database,
        tables: {}
      };
      
      for (const tableRow of tables) {
        const tableName = Object.values(tableRow)[0];
        const [structure] = await this.pool.execute(`DESCRIBE ${tableName}`);
        const [indexes] = await this.pool.execute(`SHOW INDEX FROM ${tableName}`);
        
        schema.tables[tableName] = {
          columns: structure,
          indexes: indexes
        };
      }
      
      return schema;
    } catch (error) {
      throw new Error(`Failed to get complete schema: ${error.message}`);
    }
  }

  async getTableRelationships() {
    try {
      const [relationships] = await this.pool.execute(`
        SELECT 
          TABLE_NAME,
          COLUMN_NAME,
          CONSTRAINT_NAME,
          REFERENCED_TABLE_NAME,
          REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
        WHERE REFERENCED_TABLE_NAME IS NOT NULL 
        AND TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME, COLUMN_NAME
      `);
      
      return {
        content: [
          {
            type: 'text',
            text: `Foreign Key Relationships:\n${JSON.stringify(relationships, null, 2)}`
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to get table relationships: ${error.message}`);
    }
  }

  async start() {
    try {
      // Create database connection
      await this.createConnection();
      
      // Start MCP server
      const transport = new StdioServerTransport();
      await this.server.connect(transport);
      
      console.error(`🚀 Muni MCP MySQL Server started in ${this.config.mode} mode`);
      console.error(`🔐 Security: Read-only=${this.config.security.readOnly}, Query timeout=${this.config.security.queryTimeout}ms`);
      console.error(`📊 Database: ${this.config.database.host}:${this.config.database.port}/${this.config.database.database}`);
      console.error('💬 Ready to accept queries from Claude!');
      
    } catch (error) {
      console.error('❌ Failed to start MCP server:', error.message);
      process.exit(1);
    }
  }

  async stop() {
    console.error('\n🛑 Shutting down MCP server...');
    
    if (this.pool) {
      await this.pool.end();
      console.error('🔌 Database connections closed');
    }
    
    console.error('✅ MCP server stopped');
    process.exit(0);
  }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  if (global.mcpServer) {
    await global.mcpServer.stop();
  }
});

process.on('SIGTERM', async () => {
  if (global.mcpServer) {
    await global.mcpServer.stop();
  }
});

// Start the server
async function main() {
  try {
    global.mcpServer = new MuniMySQLServer();
    await global.mcpServer.start();
  } catch (error) {
    console.error('❌ Server startup failed:', error.message);
    process.exit(1);
  }
}

// Only start if this file is run directly
if (require.main === module) {
  main().catch(error => {
    console.error('❌ Unhandled error:', error);
    process.exit(1);
  });
}

module.exports = MuniMySQLServer;