#!/usr/bin/env python3

import subprocess
import json
import re

def search_for_components_field():
    """
    Search for the components field across different JIRA projects and identify custom field IDs.
    """
    
    print("=== SEARCHING FOR COMPONENTS FIELD ===")
    
    # Test projects to search
    projects = ['TRI', 'Product Support', 'CSS1']
    
    # Try to get a comprehensive ticket view using --raw flag or other methods
    for project in projects:
        print(f"\n--- Analyzing {project} project ---")
        
        try:
            # Try to get raw JSON from a single ticket
            cmd = ['acli', 'jira', 'workitem', 'search', '--jql', f'project = "{project}"', '--limit', '1', '--json']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            if data and len(data) > 0:
                ticket = data[0]
                print(f"Sample ticket: {ticket.get('key', 'Unknown')}")
                print(f"Available fields: {list(ticket.get('fields', {}).keys())}")
                
                # Look for any field that might contain components data
                fields = ticket.get('fields', {})
                for field_name, field_value in fields.items():
                    if field_value and ('component' in str(field_value).lower() or 
                                       'category' in str(field_value).lower() or
                                       isinstance(field_value, list)):
                        print(f"  Potential components field: {field_name} = {field_value}")
                        
        except Exception as e:
            print(f"Error querying {project}: {e}")
    
    # Try to search for specific custom field patterns
    print(f"\n--- Searching for specific custom field patterns ---")
    
    # Common custom field IDs that might contain components
    custom_field_patterns = [
        'customfield_10450',  # From our urgency field analysis
        'customfield_10451',
        'customfield_10452',
        'customfield_10453',
        'customfield_10454',
        'customfield_10455'
    ]
    
    # Try to query a TRI ticket with expanded fields
    try:
        # Get one TRI ticket and examine all possible fields
        cmd = ['acli', 'jira', 'workitem', 'search', '--jql', 'project = TRI AND key = TRI-2301']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse the output to look for custom field references
        print(f"\nRaw ACLI output analysis for TRI-2301:")
        lines = result.stdout.split('\n')
        for line in lines:
            if 'customfield' in line.lower() or 'component' in line.lower():
                print(f"  Found: {line.strip()}")
                
    except Exception as e:
        print(f"Error in custom field search: {e}")

def search_urgency_field_pattern():
    """
    Since we know urgency is stored in customfield_10450, let's look for similar patterns.
    """
    
    print(f"\n=== ANALYZING CUSTOM FIELD PATTERNS ===")
    
    # We know from our previous analysis that urgency is in cf[10450]
    # Components might be in a nearby custom field
    
    # Try to export a few TRI tickets with a broader search
    try:
        # Search for tickets that might have components data
        cmd = ['acli', 'jira', 'workitem', 'search', 
               '--jql', 'project = TRI AND key in (TRI-2301, TRI-2302, TRI-2303)', 
               '--json']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        print(f"Analyzing {len(data)} TRI tickets for field patterns...")
        
        for ticket in data:
            key = ticket.get('key', 'Unknown')
            fields = ticket.get('fields', {})
            
            print(f"\n--- {key} ---")
            
            # Look for all fields that might contain array or object data (typical for components)
            for field_name, field_value in fields.items():
                if field_value is not None:
                    field_type = type(field_value).__name__
                    if field_type in ['list', 'dict'] or 'customfield' in field_name:
                        print(f"  {field_name} ({field_type}): {field_value}")
            
    except Exception as e:
        print(f"Error in pattern analysis: {e}")

def check_csv_export_for_components():
    """
    Check our existing CSV export to see if components field might already be included.
    """
    
    print(f"\n=== CHECKING EXISTING CSV FOR COMPONENTS ===")
    
    try:
        import pandas as pd
        
        csv_file = '/Users/munin8/_myprojects/tri-all-tickets-final.csv'
        df = pd.read_csv(csv_file)
        
        print(f"Existing CSV columns: {list(df.columns)}")
        
        # Check if any column might contain components data
        for col in df.columns:
            if 'component' in col.lower() or 'category' in col.lower():
                print(f"Found potential components column: {col}")
                print(f"Sample values: {df[col].value_counts().head()}")
                
        # Check if any of the existing data might actually be components
        # Look for patterns that suggest components rather than our derived categories
        if 'Issue_Category' in df.columns:
            categories = df['Issue_Category'].value_counts()
            print(f"\nCurrent Issue_Category distribution:")
            for cat, count in categories.head(10).items():
                print(f"  {cat}: {count}")
                
    except Exception as e:
        print(f"Error checking CSV: {e}")

def attempt_direct_field_query():
    """
    Try to query specific custom fields directly.
    """
    
    print(f"\n=== ATTEMPTING DIRECT FIELD QUERIES ===")
    
    # Known working: cf[10450] for urgency
    # Let's try adjacent field numbers
    field_candidates = [
        '10449', '10450', '10451', '10452', '10453', '10454', '10455'
    ]
    
    for field_id in field_candidates:
        try:
            # Try querying with specific custom field
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND cf[{field_id}] is not EMPTY',
                   '--limit', '3']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                print(f"\nCustomfield {field_id} has data:")
                print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
                
        except Exception as e:
            # Field probably doesn't exist or no data
            pass

if __name__ == "__main__":
    search_for_components_field()
    search_urgency_field_pattern()
    check_csv_export_for_components()
    attempt_direct_field_query()