#!/usr/bin/env python3

import subprocess
import json
import csv
import re

def export_with_all_possible_fields():
    """
    Try to export TRI tickets with all possible field combinations to find components.
    """
    
    print("=== COMPREHENSIVE FIELD ANALYSIS ===")
    
    # Create a comprehensive export to identify the components field
    # First, let's use our existing approach but expand the search
    
    try:
        # Export a sample of tickets with more comprehensive data
        cmd = ['acli', 'jira', 'workitem', 'search', 
               '--jql', 'project = TRI AND key in (TRI-2301, TRI-2302, TRI-2303, TRI-2294, TRI-2295)',
               '--json']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        
        print(f"Analyzing {len(data)} sample tickets for ALL fields...")
        
        # Save detailed JSON for manual inspection
        with open('/Users/munin8/_myprojects/tri_detailed_fields.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print("Detailed JSON saved to tri_detailed_fields.json")
        
        # Analyze the structure
        if data:
            sample_ticket = data[0]
            print(f"\nSample ticket {sample_ticket.get('key', 'Unknown')} has these fields:")
            fields = sample_ticket.get('fields', {})
            
            for field_name, field_value in fields.items():
                field_type = type(field_value).__name__
                if field_value is not None:
                    if isinstance(field_value, (list, dict)):
                        print(f"  {field_name} ({field_type}): {str(field_value)[:100]}...")
                    else:
                        print(f"  {field_name} ({field_type}): {field_value}")
                        
        return data
        
    except Exception as e:
        print(f"Error in comprehensive export: {e}")
        return None

def try_direct_components_export():
    """
    Try exporting with components field directly.
    """
    
    print(f"\n=== TRYING DIRECT COMPONENTS FIELD ACCESS ===")
    
    # In JIRA, components can be accessed as 'components' field
    # Let's try a different approach using our cj tool
    
    try:
        # Try using our custom jira helper
        cmd = ['python', '/Users/munin8/_myprojects/cj-buddy/jira_helper.py', 'TRI-2301']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("Custom JIRA helper output:")
        print(result.stdout[:500])
        
    except Exception as e:
        print(f"Custom helper failed: {e}")

def test_known_component_values():
    """
    Since we know there should be components from PS/CSS1, 
    let's test for typical JIRA component values.
    """
    
    print(f"\n=== TESTING FOR TYPICAL COMPONENT VALUES ===")
    
    # Common JIRA component values in support systems
    typical_components = [
        'Billing', 'Payment', 'Portal', 'Meter Reading', 'Account Management',
        'Reports', 'Integration', 'System Admin', 'Customer Service',
        'Data Export', 'Autopay', 'Late Charges', 'Rate Management'
    ]
    
    # Test these across different custom fields
    custom_fields = ['10449', '10451', '10452', '10453', '10454']
    
    for field_id in custom_fields:
        print(f"\n--- Testing cf[{field_id}] ---")
        
        for component in typical_components[:5]:  # Test first 5
            try:
                # Try exact match
                cmd = ['acli', 'jira', 'workitem', 'search', 
                       '--jql', f'project = TRI AND cf[{field_id}] = "{component}"',
                       '--count']
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                if result.stdout.strip() and '0' not in result.stdout:
                    print(f"  Found '{component}' in cf[{field_id}]: {result.stdout.strip()}")
                    
            except Exception as e:
                # Try without quotes
                try:
                    cmd = ['acli', 'jira', 'workitem', 'search', 
                           '--jql', f'project = TRI AND cf[{field_id}] = {component}',
                           '--count']
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    
                    if result.stdout.strip() and '0' not in result.stdout:
                        print(f"  Found {component} in cf[{field_id}]: {result.stdout.strip()}")
                        
                except Exception as e2:
                    pass

def analyze_field_patterns():
    """
    Analyze patterns in the fields we found to determine which might be components.
    """
    
    print(f"\n=== ANALYZING FIELD PATTERNS ===")
    
    # Based on what we know:
    # cf[10450] = Urgency (Critical, High, Medium, Low)
    # cf[10449] = ? (604 tickets have data)
    # cf[10451] = ? (585 tickets have data) 
    # cf[10452] = ? (592 tickets have data)
    
    field_analysis = {
        '10449': {'tickets': 604, 'description': 'Most populated - possible primary categorization'},
        '10450': {'tickets': 604, 'description': 'Urgency field (confirmed)'},
        '10451': {'tickets': 585, 'description': 'High population - possible components'},
        '10452': {'tickets': 592, 'description': 'High population - possible secondary categorization'},
        '10453': {'tickets': 351, 'description': 'Medium population - possible specialized field'},
        '10454': {'tickets': 208, 'description': 'Lower population - possible optional field'}
    }
    
    print("Field analysis based on population:")
    for field_id, info in field_analysis.items():
        print(f"  cf[{field_id}]: {info['tickets']} tickets - {info['description']}")
    
    # Since cf[10451] and cf[10452] have high populations and cf[10450] is urgency,
    # cf[10449], cf[10451], or cf[10452] are most likely to be components
    
    print(f"\nMost likely components field candidates: cf[10449], cf[10451], cf[10452]")
    
    return ['10449', '10451', '10452']

if __name__ == "__main__":
    data = export_with_all_possible_fields()
    try_direct_components_export()
    test_known_component_values()
    likely_fields = analyze_field_patterns()
    
    print(f"\n=== CONCLUSION ===")
    print(f"Need to extract actual values from: {likely_fields}")
    print(f"Check tri_detailed_fields.json for complete field structure")