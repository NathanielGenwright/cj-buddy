#!/usr/bin/env node

/**
 * Test Connection Script for Muni MCP MySQL Server
 * 
 * This script tests the database connections and validates that the MCP server
 * can successfully connect to the configured MySQL instances.
 */

const mysql = require('mysql2/promise');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

class ConnectionTester {
  constructor() {
    this.configs = this.loadConfigurations();
  }

  loadConfigurations() {
    return {
      development: {
        name: 'Development',
        host: process.env.MYSQL_DEV_HOST || 'localhost',
        port: parseInt(process.env.MYSQL_DEV_PORT) || 3307,
        database: process.env.MYSQL_DEV_DATABASE,
        user: process.env.MYSQL_DEV_USER,
        password: process.env.MYSQL_DEV_PASSWORD,
        // SSL disabled for Cloud SQL proxy connection
        ssl: false,
        charset: 'latin1',
        timezone: 'UTC'
      },
      test: {
        name: 'Test',
        host: process.env.MYSQL_TEST_HOST || 'localhost',
        port: parseInt(process.env.MYSQL_TEST_PORT) || 3308,
        database: process.env.MYSQL_TEST_DATABASE || 'billingdbtest',
        user: process.env.MYSQL_TEST_USER,
        password: process.env.MYSQL_TEST_PASSWORD,
        // SSL disabled for Cloud SQL proxy connection
        ssl: false,
        charset: 'latin1',
        timezone: 'UTC'
      }
    };
  }

  async testConnection(config) {
    const startTime = Date.now();
    
    try {
      console.log(`\n🔍 Testing ${config.name} database connection...`);
      console.log(`   Host: ${config.host}:${config.port}`);
      console.log(`   Database: ${config.database || 'Not specified'}`);
      console.log(`   User: ${config.user || 'Not specified'}`);
      
      if (!config.user || !config.password) {
        throw new Error('Missing database credentials');
      }
      
      const connection = await mysql.createConnection({
        host: config.host,
        port: config.port,
        user: config.user,
        password: config.password,
        database: config.database,
        ssl: config.ssl,
        charset: config.charset,
        timezone: config.timezone,
        connectTimeout: 10000,
        acquireTimeout: 10000
      });
      
      // Test basic connection
      const [versionRows] = await connection.execute('SELECT VERSION() as version, DATABASE() as current_database');
      const version = versionRows[0];
      
      // Test permissions
      const [permissionRows] = await connection.execute('SHOW GRANTS');
      
      // Get table count
      let tableCount = 0;
      try {
        const [tableRows] = await connection.execute('SHOW TABLES');
        tableCount = tableRows.length;
      } catch (error) {
        console.log(`   ⚠️  Could not count tables: ${error.message}`);
      }
      
      await connection.end();
      
      const duration = Date.now() - startTime;
      
      console.log(`   ✅ Connection successful (${duration}ms)`);
      console.log(`   📊 MySQL Version: ${version.version}`);
      // Server time removed due to SQL compatibility
      console.log(`   🗄️  Current Database: ${version.current_database || 'None selected'}`);
      console.log(`   📋 Table Count: ${tableCount}`);
      console.log(`   🔐 Permissions: ${permissionRows.length} grants found`);
      
      return {
        success: true,
        config: config.name,
        duration,
        version: version.version,
        database: version.current_database,
        tableCount,
        grants: permissionRows.length
      };
      
    } catch (error) {
      const duration = Date.now() - startTime;
      console.log(`   ❌ Connection failed (${duration}ms): ${error.message}`);
      
      // Additional error context
      if (error.code) {
        console.log(`   🔍 Error Code: ${error.code}`);
      }
      if (error.errno) {
        console.log(`   🔢 Error Number: ${error.errno}`);
      }
      
      return {
        success: false,
        config: config.name,
        duration,
        error: error.message,
        code: error.code,
        errno: error.errno
      };
    }
  }

  async testAllConnections() {
    console.log('🧪 Starting database connection tests...');
    console.log('=' .repeat(50));
    
    const results = [];
    
    // Only test development database (test database is disabled)
    const result = await this.testConnection(this.configs.development);
    results.push(result);
    
    console.log('\n' + '=' .repeat(50));
    console.log('📊 Test Results Summary:');
    
    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);
    
    console.log(`\n✅ Successful connections: ${successful.length}/${results.length}`);
    
    successful.forEach(result => {
      console.log(`   • ${result.config}: MySQL ${result.version} (${result.tableCount} tables)`);
    });
    
    if (failed.length > 0) {
      console.log(`\n❌ Failed connections: ${failed.length}/${results.length}`);
      
      failed.forEach(result => {
        console.log(`   • ${result.config}: ${result.error}`);
      });
    }
    
    console.log(`\n⏱️  Average connection time: ${Math.round(results.reduce((sum, r) => sum + r.duration, 0) / results.length)}ms`);
    
    return {
      total: results.length,
      successful: successful.length,
      failed: failed.length,
      results
    };
  }

  async testMCPServerQueries() {
    console.log('\n🧪 Testing MCP-style queries...');
    console.log('=' .repeat(50));
    
    // Test with development database
    const config = this.configs.development;
    
    if (!config.user || !config.password) {
      console.log('❌ Skipping query tests - missing development database credentials');
      return;
    }
    
    try {
      const connection = await mysql.createConnection({
        host: config.host,
        port: config.port,
        user: config.user,
        password: config.password,
        database: config.database,
        ssl: config.ssl,
        charset: config.charset,
        timezone: config.timezone
      });
      
      console.log('\n🔍 Testing common MCP queries...');
      
      // Test queries that MCP server would use
      const testQueries = [
        {
          name: 'Show Tables',
          sql: 'SHOW TABLES'
        },
        {
          name: 'Database Info',
          sql: 'SELECT DATABASE() as current_database, VERSION() as version, @@character_set_database as charset'
        },
        {
          name: 'Table Count',
          sql: 'SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = DATABASE()'
        }
      ];
      
      for (const query of testQueries) {
        try {
          const startTime = Date.now();
          const [rows] = await connection.execute(query.sql);
          const duration = Date.now() - startTime;
          
          console.log(`   ✅ ${query.name}: ${rows.length} rows (${duration}ms)`);
        } catch (error) {
          console.log(`   ❌ ${query.name}: ${error.message}`);
        }
      }
      
      // Test describe table if tables exist
      try {
        const [tables] = await connection.execute('SHOW TABLES');
        if (tables.length > 0) {
          const tableName = Object.values(tables[0])[0];
          const startTime = Date.now();
          const [structure] = await connection.execute(`DESCRIBE ${tableName}`);
          const duration = Date.now() - startTime;
          
          console.log(`   ✅ Describe Table (${tableName}): ${structure.length} columns (${duration}ms)`);
        }
      } catch (error) {
        console.log(`   ⚠️  Could not test table description: ${error.message}`);
      }
      
      await connection.end();
      
    } catch (error) {
      console.log(`❌ Query testing failed: ${error.message}`);
    }
  }

  printEnvironmentInfo() {
    console.log('\n🔧 Environment Configuration:');
    console.log('=' .repeat(50));
    
    const envVars = [
      'MYSQL_DEV_HOST',
      'MYSQL_DEV_PORT', 
      'MYSQL_DEV_DATABASE',
      'MYSQL_DEV_USER',
      'MYSQL_TEST_HOST',
      'MYSQL_TEST_PORT',
      'MYSQL_TEST_DATABASE', 
      'MYSQL_TEST_USER',
      'MCP_SSL_MODE',
      'MCP_READ_ONLY',
      'MCP_MAX_CONNECTIONS'
    ];
    
    envVars.forEach(varName => {
      const value = process.env[varName];
      const displayValue = varName.includes('PASSWORD') ? '***' : (value || 'Not set');
      console.log(`   ${varName}: ${displayValue}`);
    });
  }
}

async function main() {
  try {
    const tester = new ConnectionTester();
    
    // Show environment info
    tester.printEnvironmentInfo();
    
    // Test connections
    const summary = await tester.testAllConnections();
    
    // Test MCP queries
    await tester.testMCPServerQueries();
    
    console.log('\n🏁 Testing complete!');
    
    if (summary.failed > 0) {
      console.log('\n⚠️  Some connections failed. Check your .env configuration and ensure Docker containers are running.');
      process.exit(1);
    } else {
      console.log('\n🎉 All connections successful! MCP server should work properly.');
      process.exit(0);
    }
    
  } catch (error) {
    console.error('\n❌ Test runner failed:', error.message);
    process.exit(1);
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  main();
}

module.exports = ConnectionTester;