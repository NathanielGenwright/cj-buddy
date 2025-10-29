#!/usr/bin/env python3

import subprocess
import json
import csv
import re

def extract_custom_field_values():
    """
    Extract actual values from custom fields to identify which one contains components data.
    """
    
    print("=== EXTRACTING CUSTOM FIELD VALUES ===")
    
    # Fields that have data
    custom_fields = ['10449', '10450', '10451', '10452', '10453', '10454']
    
    for field_id in custom_fields:
        print(f"\n--- CUSTOM FIELD {field_id} ---")
        
        try:
            # Get a sample of tickets with this field populated
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND cf[{field_id}] is not EMPTY',
                   '--limit', '10']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the output to extract field values
            lines = result.stdout.strip().split('\n')
            print(f"Sample tickets with cf[{field_id}]:")
            for line in lines[:5]:  # Show first 5 tickets
                print(f"  {line}")
                
            # Also check for distinct values
            try:
                # Try to get unique values for this field
                cmd2 = ['acli', 'jira', 'workitem', 'search', 
                        '--jql', f'project = TRI AND cf[{field_id}] is not EMPTY',
                        '--limit', '50']
                result2 = subprocess.run(cmd2, capture_output=True, text=True, check=True)
                
                if result2.stdout:
                    print(f"Field {field_id} has data in {len(result2.stdout.strip().split())} tickets")
                    
            except Exception as e:
                print(f"  Could not get extended data: {e}")
                
        except Exception as e:
            print(f"  Error querying cf[{field_id}]: {e}")

def try_jql_with_field_values():
    """
    Try JQL queries to understand what values are in these custom fields.
    """
    
    print(f"\n=== TRYING JQL QUERIES FOR FIELD VALUES ===")
    
    # Try to search for common component-like values
    component_terms = [
        'Billing', 'Payment', 'Portal', 'System', 'Integration', 
        'Meter', 'Data', 'Account', 'Customer', 'Report'
    ]
    
    custom_fields = ['10449', '10450', '10451', '10452', '10453', '10454']
    
    for field_id in custom_fields:
        print(f"\n--- Testing cf[{field_id}] for component-like values ---")
        
        for term in component_terms[:3]:  # Test first few terms
            try:
                cmd = ['acli', 'jira', 'workitem', 'search', 
                       '--jql', f'project = TRI AND cf[{field_id}] ~ "{term}"',
                       '--count']
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                if result.stdout.strip() and '0' not in result.stdout:
                    print(f"  cf[{field_id}] contains '{term}': {result.stdout.strip()}")
                    
            except Exception as e:
                # Field might not support text search
                pass

def analyze_urgency_field_for_pattern():
    """
    Since we know cf[10450] is urgency, let's see its values to understand the pattern.
    """
    
    print(f"\n=== ANALYZING KNOWN URGENCY FIELD (cf[10450]) ===")
    
    try:
        # Get tickets with different urgency values
        urgency_values = ['Critical', 'High', 'Medium', 'Low']
        
        for urgency in urgency_values:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND cf[10450] = "{urgency}"',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                print(f"  Urgency '{urgency}': {result.stdout.strip()} tickets")
                
    except Exception as e:
        print(f"Error analyzing urgency field: {e}")

def create_comprehensive_export():
    """
    Create a comprehensive export to extract all custom field data.
    """
    
    print(f"\n=== CREATING COMPREHENSIVE EXPORT ===")
    
    try:
        # Export TRI tickets with attempt to capture custom field data
        # We'll parse the raw output to find custom field patterns
        
        cmd = ['acli', 'jira', 'workitem', 'search', 
               '--jql', 'project = TRI',
               '--limit', '20']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Save raw output for analysis
        with open('/Users/munin8/_myprojects/tri_raw_export.txt', 'w') as f:
            f.write(result.stdout)
        
        print("Raw export saved to tri_raw_export.txt")
        
        # Look for patterns in the output
        lines = result.stdout.split('\n')
        for i, line in enumerate(lines[:20]):
            if any(term in line.lower() for term in ['component', 'category', 'billing', 'payment']):
                print(f"  Potential match line {i}: {line}")
                
    except Exception as e:
        print(f"Error creating export: {e}")

if __name__ == "__main__":
    extract_custom_field_values()
    try_jql_with_field_values()
    analyze_urgency_field_for_pattern()
    create_comprehensive_export()