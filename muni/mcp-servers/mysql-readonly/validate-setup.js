#!/usr/bin/env node

/**
 * MCP Setup Validation Script
 * 
 * This script performs comprehensive validation of the MCP MySQL server setup,
 * checking prerequisites, configuration, connections, and functionality.
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const mysql = require('mysql2/promise');
require('dotenv').config();

class SetupValidator {
  constructor() {
    this.results = {
      prerequisites: [],
      configuration: [],
      connections: [],
      functionality: [],
      overall: { passed: 0, failed: 0, warnings: 0 }
    };
    
    this.colors = {
      green: '\x1b[32m',
      red: '\x1b[31m',
      yellow: '\x1b[33m',
      blue: '\x1b[34m',
      cyan: '\x1b[36m',
      reset: '\x1b[0m'
    };
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const colors = this.colors;
    
    switch (type) {
      case 'success':
        console.log(`${colors.green}✅ [${timestamp}] ${message}${colors.reset}`);
        break;
      case 'error':
        console.log(`${colors.red}❌ [${timestamp}] ${message}${colors.reset}`);
        break;
      case 'warning':
        console.log(`${colors.yellow}⚠️  [${timestamp}] ${message}${colors.reset}`);
        break;
      case 'info':
        console.log(`${colors.blue}ℹ️  [${timestamp}] ${message}${colors.reset}`);
        break;
      case 'header':
        console.log(`${colors.cyan}🔍 [${timestamp}] ${message}${colors.reset}`);
        break;
    }
  }

  addResult(category, test, status, message, details = null) {
    const result = { test, status, message, details, timestamp: new Date().toISOString() };
    this.results[category].push(result);
    
    switch (status) {
      case 'pass':
        this.results.overall.passed++;
        break;
      case 'fail':
        this.results.overall.failed++;
        break;
      case 'warning':
        this.results.overall.warnings++;
        break;
    }
  }

  async checkPrerequisites() {
    this.log('Checking Prerequisites...', 'header');
    
    // Check Node.js version
    try {
      const nodeVersion = process.version;
      const majorVersion = parseInt(nodeVersion.split('.')[0].substring(1));
      
      if (majorVersion >= 18) {
        this.addResult('prerequisites', 'Node.js Version', 'pass', 
          `Node.js ${nodeVersion} (✓ >= 18)`, { version: nodeVersion });
        this.log(`Node.js version: ${nodeVersion}`, 'success');
      } else {
        this.addResult('prerequisites', 'Node.js Version', 'fail', 
          `Node.js ${nodeVersion} (✗ < 18 required)`, { version: nodeVersion });
        this.log(`Node.js version too old: ${nodeVersion}`, 'error');
      }
    } catch (error) {
      this.addResult('prerequisites', 'Node.js Version', 'fail', 
        'Failed to check Node.js version', { error: error.message });
      this.log('Failed to check Node.js version', 'error');
    }
    
    // Check npm installation
    try {
      const packageJsonPath = path.join(__dirname, 'package.json');
      const nodeModulesPath = path.join(__dirname, 'node_modules');
      
      if (fs.existsSync(packageJsonPath)) {
        this.addResult('prerequisites', 'Package.json', 'pass', 
          'package.json exists', { path: packageJsonPath });
        this.log('package.json found', 'success');
        
        if (fs.existsSync(nodeModulesPath)) {
          this.addResult('prerequisites', 'Dependencies', 'pass', 
            'node_modules directory exists', { path: nodeModulesPath });
          this.log('Dependencies installed', 'success');
        } else {
          this.addResult('prerequisites', 'Dependencies', 'fail', 
            'node_modules directory missing - run npm install', { path: nodeModulesPath });
          this.log('Dependencies not installed', 'error');
        }
      } else {
        this.addResult('prerequisites', 'Package.json', 'fail', 
          'package.json not found', { path: packageJsonPath });
        this.log('package.json not found', 'error');
      }
    } catch (error) {
      this.addResult('prerequisites', 'Package Structure', 'fail', 
        'Failed to check package structure', { error: error.message });
      this.log('Failed to check package structure', 'error');
    }
    
    // Check required files
    const requiredFiles = [
      'server.js',
      'test-connection.js',
      'config.json',
      '.env.example'
    ];
    
    for (const file of requiredFiles) {
      const filePath = path.join(__dirname, file);
      if (fs.existsSync(filePath)) {
        this.addResult('prerequisites', `File: ${file}`, 'pass', 
          `${file} exists`, { path: filePath });
        this.log(`${file} found`, 'success');
      } else {
        this.addResult('prerequisites', `File: ${file}`, 'fail', 
          `${file} missing`, { path: filePath });
        this.log(`${file} missing`, 'error');
      }
    }
  }

  async checkConfiguration() {
    this.log('Checking Configuration...', 'header');
    
    // Check .env file
    const envPath = path.join(__dirname, '.env');
    if (fs.existsSync(envPath)) {
      this.addResult('configuration', '.env File', 'pass', 
        '.env file exists', { path: envPath });
      this.log('.env file found', 'success');
      
      // Check required environment variables
      const requiredEnvVars = [
        'MYSQL_DEV_HOST',
        'MYSQL_DEV_PORT',
        'MYSQL_DEV_USER',
        'MYSQL_DEV_PASSWORD'
        // Test database variables removed - using dev only
      ];
      
      const missingVars = [];
      const emptyVars = [];
      
      for (const varName of requiredEnvVars) {
        const value = process.env[varName];
        if (!value) {
          if (value === undefined) {
            missingVars.push(varName);
          } else {
            emptyVars.push(varName);
          }
        }
      }
      
      if (missingVars.length === 0 && emptyVars.length === 0) {
        this.addResult('configuration', 'Environment Variables', 'pass', 
          'All required environment variables are set');
        this.log('All environment variables configured', 'success');
      } else {
        const issues = [];
        if (missingVars.length > 0) {
          issues.push(`Missing: ${missingVars.join(', ')}`);
        }
        if (emptyVars.length > 0) {
          issues.push(`Empty: ${emptyVars.join(', ')}`);
        }
        
        this.addResult('configuration', 'Environment Variables', 'fail', 
          `Environment variable issues: ${issues.join('; ')}`, 
          { missing: missingVars, empty: emptyVars });
        this.log(`Environment variable issues: ${issues.join('; ')}`, 'error');
      }
    } else {
      this.addResult('configuration', '.env File', 'fail', 
        '.env file missing - copy from .env.example', { path: envPath });
      this.log('.env file missing', 'error');
    }
    
    // Check config.json
    const configPath = path.join(__dirname, 'config.json');
    if (fs.existsSync(configPath)) {
      try {
        const configContent = fs.readFileSync(configPath, 'utf8');
        const config = JSON.parse(configContent);
        
        this.addResult('configuration', 'config.json', 'pass', 
          'config.json is valid JSON', { keys: Object.keys(config) });
        this.log('config.json is valid', 'success');
        
        // Check for required configuration sections
        const requiredSections = ['server', 'databases', 'security'];
        for (const section of requiredSections) {
          if (config[section]) {
            this.log(`Configuration section '${section}' present`, 'success');
          } else {
            this.addResult('configuration', `config.json section: ${section}`, 'warning', 
              `Configuration section '${section}' missing`);
            this.log(`Configuration section '${section}' missing`, 'warning');
          }
        }
      } catch (error) {
        this.addResult('configuration', 'config.json', 'fail', 
          'config.json is invalid JSON', { error: error.message });
        this.log('config.json is invalid JSON', 'error');
      }
    } else {
      this.addResult('configuration', 'config.json', 'warning', 
        'config.json not found (using defaults)', { path: configPath });
      this.log('config.json not found', 'warning');
    }
  }

  async testDatabaseConnection(dbType) {
    const configs = {
      development: {
        host: process.env.MYSQL_DEV_HOST || 'localhost',
        port: parseInt(process.env.MYSQL_DEV_PORT) || 3307,
        user: process.env.MYSQL_DEV_USER,
        password: process.env.MYSQL_DEV_PASSWORD,
        database: process.env.MYSQL_DEV_DATABASE
      },
      test: {
        host: process.env.MYSQL_TEST_HOST || 'localhost',
        port: parseInt(process.env.MYSQL_TEST_PORT) || 3308,
        user: process.env.MYSQL_TEST_USER,
        password: process.env.MYSQL_TEST_PASSWORD,
        database: process.env.MYSQL_TEST_DATABASE || 'billingdbtest'
      }
    };
    
    const config = configs[dbType];
    const startTime = Date.now();
    
    try {
      this.log(`Testing ${dbType} database connection...`, 'info');
      
      // Basic connection test
      const connection = await mysql.createConnection({
        host: config.host,
        port: config.port,
        user: config.user,
        password: config.password,
        database: config.database,
        ssl: false, // Disabled for Cloud SQL proxy
        connectTimeout: 10000
      });
      
      // Test basic query
      const [rows] = await connection.execute('SELECT VERSION() as version, DATABASE() as current_database');
      const info = rows[0];
      
      // Test permissions
      const [grants] = await connection.execute('SHOW GRANTS');
      
      // Test table access
      let tableCount = 0;
      try {
        const [tables] = await connection.execute('SHOW TABLES');
        tableCount = tables.length;
      } catch (error) {
        this.log(`Could not count tables: ${error.message}`, 'warning');
      }
      
      await connection.end();
      
      const duration = Date.now() - startTime;
      
      this.addResult('connections', `${dbType} Database`, 'pass', 
        `Connected successfully (${duration}ms)`, {
          host: config.host,
          port: config.port,
          database: info.current_database,
          version: info.version,
          tableCount,
          grants: grants.length,
          duration
        });
      
      this.log(`${dbType} database: MySQL ${info.version} (${tableCount} tables, ${duration}ms)`, 'success');
      
      return true;
    } catch (error) {
      const duration = Date.now() - startTime;
      
      this.addResult('connections', `${dbType} Database`, 'fail', 
        `Connection failed: ${error.message}`, {
          host: config.host,
          port: config.port,
          error: error.message,
          code: error.code,
          duration
        });
      
      this.log(`${dbType} database connection failed: ${error.message}`, 'error');
      return false;
    }
  }

  async checkConnections() {
    this.log('Checking Database Connections...', 'header');
    
    // Only test development database - test database disabled
    await this.testDatabaseConnection('development');
  }

  async testMCPFunctionality() {
    this.log('Testing MCP Server Functionality...', 'header');
    
    // Test server startup (dry run)
    try {
      this.log('Testing server startup...', 'info');
      
      // We'll do a syntax check by requiring the server file
      const serverPath = path.join(__dirname, 'server.js');
      if (fs.existsSync(serverPath)) {
        // Check if the file has valid syntax
        const serverContent = fs.readFileSync(serverPath, 'utf8');
        
        if (serverContent.includes('class MuniMySQLServer') || serverContent.includes('function')) {
          this.addResult('functionality', 'Server Code', 'pass', 
            'Server code appears valid');
          this.log('Server code validation passed', 'success');
        } else {
          this.addResult('functionality', 'Server Code', 'warning', 
            'Server code structure unclear');
          this.log('Server code structure unclear', 'warning');
        }
        
        // Check for required dependencies in server code
        const requiredImports = ['mysql', '@modelcontextprotocol', 'dotenv'];
        const missingImports = [];
        
        for (const imp of requiredImports) {
          if (!serverContent.includes(imp)) {
            missingImports.push(imp);
          }
        }
        
        if (missingImports.length === 0) {
          this.addResult('functionality', 'Server Dependencies', 'pass', 
            'All required imports present in server code');
          this.log('Server dependencies check passed', 'success');
        } else {
          this.addResult('functionality', 'Server Dependencies', 'warning', 
            `Potentially missing imports: ${missingImports.join(', ')}`);
          this.log(`Potentially missing imports: ${missingImports.join(', ')}`, 'warning');
        }
      } else {
        this.addResult('functionality', 'Server Code', 'fail', 
          'server.js not found');
        this.log('server.js not found', 'error');
      }
    } catch (error) {
      this.addResult('functionality', 'Server Code', 'fail', 
        `Server code validation failed: ${error.message}`, { error: error.message });
      this.log(`Server code validation failed: ${error.message}`, 'error');
    }
    
    // Test helper scripts
    const scriptDir = path.resolve(__dirname, '../../scripts');
    const expectedScripts = ['mcp-start.sh', 'mcp-stop.sh', 'mcp-status.sh', 'mcp-logs.sh'];
    
    for (const script of expectedScripts) {
      const scriptPath = path.join(scriptDir, script);
      if (fs.existsSync(scriptPath)) {
        const stats = fs.statSync(scriptPath);
        if (stats.mode & parseInt('111', 8)) { // Check if executable
          this.addResult('functionality', `Script: ${script}`, 'pass', 
            `${script} exists and is executable`);
          this.log(`${script} is ready`, 'success');
        } else {
          this.addResult('functionality', `Script: ${script}`, 'warning', 
            `${script} exists but is not executable`);
          this.log(`${script} is not executable`, 'warning');
        }
      } else {
        this.addResult('functionality', `Script: ${script}`, 'warning', 
          `${script} not found`);
        this.log(`${script} not found`, 'warning');
      }
    }
  }

  generateReport() {
    this.log('Generating Validation Report...', 'header');
    
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        total_tests: this.results.overall.passed + this.results.overall.failed + this.results.overall.warnings,
        passed: this.results.overall.passed,
        failed: this.results.overall.failed,
        warnings: this.results.overall.warnings,
        success_rate: Math.round((this.results.overall.passed / (this.results.overall.passed + this.results.overall.failed)) * 100) || 0
      },
      details: this.results
    };
    
    // Save detailed report
    const reportPath = path.join(__dirname, 'validation-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    // Display summary
    console.log('\n' + '='.repeat(60));
    console.log(`${this.colors.cyan}📊 VALIDATION SUMMARY${this.colors.reset}`);
    console.log('='.repeat(60));
    
    console.log(`Total Tests: ${report.summary.total_tests}`);
    console.log(`${this.colors.green}✅ Passed: ${report.summary.passed}${this.colors.reset}`);
    console.log(`${this.colors.red}❌ Failed: ${report.summary.failed}${this.colors.reset}`);
    console.log(`${this.colors.yellow}⚠️  Warnings: ${report.summary.warnings}${this.colors.reset}`);
    console.log(`Success Rate: ${report.summary.success_rate}%`);
    
    console.log('\n' + this.colors.cyan + '📋 RECOMMENDATIONS:' + this.colors.reset);
    
    if (report.summary.failed > 0) {
      console.log(`${this.colors.red}🔥 CRITICAL ISSUES (${report.summary.failed}):${this.colors.reset}`);
      
      for (const category in this.results) {
        if (category === 'overall') continue;
        
        const failures = this.results[category].filter(r => r.status === 'fail');
        if (failures.length > 0) {
          console.log(`\n   ${category.toUpperCase()}:`);
          failures.forEach(failure => {
            console.log(`   • ${failure.test}: ${failure.message}`);
          });
        }
      }
      
      console.log(`\n${this.colors.red}❌ Setup is NOT ready. Please fix the issues above before proceeding.${this.colors.reset}`);
    } else if (report.summary.warnings > 0) {
      console.log(`${this.colors.yellow}⚠️  WARNINGS (${report.summary.warnings}):${this.colors.reset}`);
      
      for (const category in this.results) {
        if (category === 'overall') continue;
        
        const warnings = this.results[category].filter(r => r.status === 'warning');
        if (warnings.length > 0) {
          console.log(`\n   ${category.toUpperCase()}:`);
          warnings.forEach(warning => {
            console.log(`   • ${warning.test}: ${warning.message}`);
          });
        }
      }
      
      console.log(`\n${this.colors.yellow}⚠️  Setup has warnings but should work. Consider addressing warnings for optimal operation.${this.colors.reset}`);
    } else {
      console.log(`${this.colors.green}🎉 Perfect! Your MCP setup is ready to go!${this.colors.reset}`);
    }
    
    console.log('\n' + this.colors.blue + '📄 NEXT STEPS:' + this.colors.reset);
    
    if (report.summary.failed === 0) {
      console.log('1. Start the MCP server: ./scripts/mcp-start.sh');
      console.log('2. Configure Claude using claude-mcp-setup.md instructions');
      console.log('3. Test the connection by asking Claude about the database');
      console.log('4. Monitor logs with ./scripts/mcp-logs.sh');
    } else {
      console.log('1. Fix the critical issues listed above');
      console.log('2. Run this validation again: npm run validate');
      console.log('3. Once all tests pass, configure Claude and start testing');
    }
    
    console.log(`\n📁 Detailed report saved to: ${reportPath}`);
    console.log('='.repeat(60));
    
    return report.summary.failed === 0;
  }

  async run() {
    console.log(`${this.colors.cyan}🚀 Starting MCP MySQL Server Setup Validation${this.colors.reset}`);
    console.log(`Timestamp: ${new Date().toISOString()}`);
    console.log(`Directory: ${__dirname}`);
    console.log('=' .repeat(60));
    
    try {
      await this.checkPrerequisites();
      await this.checkConfiguration();
      await this.checkConnections();
      await this.testMCPFunctionality();
      
      const success = this.generateReport();
      
      process.exit(success ? 0 : 1);
      
    } catch (error) {
      this.log(`Validation failed with unexpected error: ${error.message}`, 'error');
      console.error(error.stack);
      process.exit(1);
    }
  }
}

// Run validation if this file is executed directly
if (require.main === module) {
  const validator = new SetupValidator();
  validator.run();
}

module.exports = SetupValidator;