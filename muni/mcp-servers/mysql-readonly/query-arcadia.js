#!/usr/bin/env node

/**
 * Quick query to find customers in Arcadia
 */

const mysql = require('mysql2/promise');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

async function queryArcadiaCustomers() {
  try {
    console.log('🔍 Connecting to database...');
    
    const connection = await mysql.createConnection({
      host: process.env.MYSQL_DEV_HOST || 'localhost',
      port: parseInt(process.env.MYSQL_DEV_PORT) || 3307,
      user: process.env.MYSQL_DEV_USER,
      password: process.env.MYSQL_DEV_PASSWORD,
      database: process.env.MYSQL_DEV_DATABASE,
      ssl: false
    });
    
    console.log('✅ Connected! Exploring customer tables...');
    
    // First, let's see what customer-related tables exist
    const [tables] = await connection.execute("SHOW TABLES LIKE '%customer%'");
    console.log('\n📋 Customer-related tables:');
    tables.forEach(table => {
      const tableName = Object.values(table)[0];
      console.log(`  • ${tableName}`);
    });
    
    // Look specifically for the main 'customers' table
    const customersTable = tables.find(table => Object.values(table)[0] === 'customers');
    
    if (customersTable) {
      const customerTable = 'customers';
      
      // Let's see the structure of the customers table
      console.log(`\n🔍 Structure of ${customerTable} table:`);
      const [structure] = await connection.execute(`DESCRIBE ${customerTable}`);
      structure.forEach(field => {
        console.log(`  • ${field.Field} (${field.Type})`);
      });
      
      // Look for city-related columns
      const cityColumns = structure.filter(field => 
        field.Field.toLowerCase().includes('city') || 
        field.Field.toLowerCase().includes('address')
      );
      
      if (cityColumns.length > 0) {
        console.log(`\n🏙️  City-related columns found:`);
        cityColumns.forEach(col => {
          console.log(`  • ${col.Field}`);
        });
        
        // Try to query for Arcadia customers
        const cityColumn = cityColumns.find(col => col.Field.toLowerCase().includes('city'))?.Field;
        
        if (cityColumn) {
          console.log(`\n🎯 Searching for customers in Arcadia using column: ${cityColumn}`);
          
          const [results] = await connection.execute(
            `SELECT COUNT(*) as customer_count FROM ${customerTable} WHERE ${cityColumn} LIKE '%Arcadia%'`
          );
          
          const count = results[0].customer_count;
          console.log(`\n🎉 ANSWER: There are ${count} customers in the city of Arcadia!`);
          
          // Let's also see a sample of the cities to make sure we're getting the right data
          console.log(`\n📊 Sample cities in the database:`);
          const [sampleCities] = await connection.execute(
            `SELECT DISTINCT ${cityColumn} as city, COUNT(*) as count 
             FROM ${customerTable} 
             WHERE ${cityColumn} IS NOT NULL 
             GROUP BY ${cityColumn} 
             ORDER BY count DESC 
             LIMIT 10`
          );
          
          sampleCities.forEach(row => {
            console.log(`  • ${row.city}: ${row.count} customers`);
          });
          
        } else {
          console.log('\n❌ No city column found in the customers table');
        }
      } else {
        console.log('\n❌ No city-related columns found in the customers table');
        
        // Let's see what columns we do have
        console.log('\nAvailable columns:');
        structure.forEach(field => {
          console.log(`  • ${field.Field}`);
        });
      }
      
    } else {
      console.log('\n❌ No customer-related tables found');
      
      // Let's see what tables are available
      console.log('\n📋 All available tables:');
      const [allTables] = await connection.execute('SHOW TABLES LIMIT 20');
      allTables.forEach(table => {
        const tableName = Object.values(table)[0];
        console.log(`  • ${tableName}`);
      });
    }
    
    await connection.end();
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

queryArcadiaCustomers();