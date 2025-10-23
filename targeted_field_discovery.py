#!/usr/bin/env python3

import subprocess
import json
import datetime

def test_specific_field_range():
    """
    Test a targeted range of custom fields for TRI-1858.
    """
    
    print("=== TARGETED CUSTOM FIELD DISCOVERY ===")
    print("Testing TRI-1858 for custom fields...")
    
    # Test specific ranges more efficiently
    test_fields = list(range(10440, 10470)) + list(range(10400, 10440))
    
    found_fields = {}
    
    print(f"Testing {len(test_fields)} custom fields...")
    
    for i, field_id in enumerate(test_fields):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(test_fields)} fields tested")
        
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND key = TRI-1858 AND cf[{field_id}] is not EMPTY',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
            
            if '1' in result.stdout:
                print(f"  ✅ cf[{field_id}] has data in TRI-1858")
                found_fields[field_id] = True
                
        except Exception as e:
            continue
    
    return found_fields

def analyze_known_fields():
    """
    Focus on analyzing the fields we know have data.
    """
    
    print(f"\n=== ANALYZING KNOWN FIELDS ===")
    
    # Confirmed fields from our previous analysis
    known_fields = {
        10449: {'name': 'Components', 'confirmed': True},
        10450: {'name': 'Urgency', 'value': 'High', 'confirmed': True},
        10451: {'name': 'Impact', 'confirmed': True}
    }
    
    field_analysis = {}
    
    for field_id, info in known_fields.items():
        print(f"\n--- Analyzing cf[{field_id}] ({info['name']}) ---")
        
        if info.get('value'):
            field_analysis[field_id] = {
                'name': info['name'],
                'value': info['value'],
                'method': 'previously_confirmed'
            }
            print(f"  Value: {info['value']} (previously confirmed)")
            continue
        
        # Try to extract value for this field
        value = extract_field_value(field_id, info['name'])
        
        field_analysis[field_id] = {
            'name': info['name'],
            'value': value if value else 'UNKNOWN',
            'method': 'extraction_attempted'
        }
        
        if value:
            print(f"  ✅ Extracted value: {value}")
        else:
            print(f"  ❌ Could not extract value")
    
    return field_analysis

def extract_field_value(field_id, field_name):
    """
    Try to extract the actual value for a specific field.
    """
    
    # Strategy 1: Test common values
    test_values = []
    
    if field_name == 'Components':
        test_values = [
            'Billing System', 'Payment Processing', 'Customer Portal', 
            'Account Management', 'Meter Reading', 'Data Management',
            'System Administration', 'Integration', 'Reports', 'Communication',
            'Billing', 'Payment', 'Portal', 'Meter', 'Data', 'System'
        ]
    elif field_name == 'Impact':
        test_values = ['Critical', 'High', 'Medium', 'Low', '1', '2', '3', '4']
    
    for value in test_values:
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND key = TRI-1858 AND cf[{field_id}] = "{value}"',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=3)
            
            if '1' in result.stdout:
                return value
                
        except Exception as e:
            continue
    
    # Strategy 2: Try to infer from summary analysis
    if field_name == 'Components':
        # TRI-1858 summary: "CID 1769: Durango West Metro District: Unpost Meter Reading with end date 03/31/25"
        # This suggests Meter Reading component
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND key = TRI-1858 AND cf[{field_id}] = "Meter Reading"',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=3)
            
            if '1' in result.stdout:
                return "Meter Reading"
        except:
            pass
    
    return None

def create_simple_mapping():
    """
    Create a simple mapping document with what we know.
    """
    
    print(f"\n=== CREATING FIELD MAPPING ===")
    
    mapping = {
        'confirmed_fields': {
            10449: {'name': 'Components', 'value': 'UNKNOWN', 'confidence': 'Medium'},
            10450: {'name': 'Urgency', 'value': 'High', 'confidence': 'High'},
            10451: {'name': 'Impact', 'value': 'UNKNOWN', 'confidence': 'Medium'}
        },
        'company_field': 'NOT_FOUND',
        'reference_ticket': 'TRI-1858',
        'analysis_date': datetime.datetime.now().isoformat()
    }
    
    # Save mapping
    with open('/Users/munin8/_myprojects/tri_field_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    # Create readable report
    report_file = '/Users/munin8/_myprojects/tri_field_mapping_summary.md'
    
    with open(report_file, 'w') as f:
        f.write("# TRI Custom Field Mapping Summary\n\n")
        f.write(f"**Reference Ticket**: TRI-1858\n")
        f.write(f"**Analysis Date**: {mapping['analysis_date']}\n\n")
        
        f.write("## Confirmed Field Mappings\n\n")
        f.write("| Field ID | Field Name | TRI-1858 Value | Confidence |\n")
        f.write("|----------|------------|----------------|------------|\n")
        
        for field_id, data in mapping['confirmed_fields'].items():
            f.write(f"| cf[{field_id}] | {data['name']} | {data['value']} | {data['confidence']} |\n")
        
        f.write(f"\n## Status\n\n")
        f.write(f"- **Components Field**: cf[10449] (value extraction pending)\n")
        f.write(f"- **Urgency Field**: cf[10450] = 'High' ✅\n")
        f.write(f"- **Impact Field**: cf[10451] (value extraction pending)\n")
        f.write(f"- **Company Field**: Not yet identified ❌\n")
        
        f.write(f"\n## Next Steps\n\n")
        f.write(f"1. Use alternative methods to extract Components and Impact values\n")
        f.write(f"2. Search for Company field in broader range or different approach\n")
        f.write(f"3. Proceed with analysis using available field mappings\n")
    
    print(f"Mapping saved to: {report_file}")
    return mapping

def main():
    """
    Main execution with focused approach.
    """
    
    print("=== FOCUSED FIELD DISCOVERY FOR TRI-1858 ===")
    
    # Step 1: Quick test of additional fields
    additional_fields = test_specific_field_range()
    
    # Step 2: Analyze known fields
    field_analysis = analyze_known_fields()
    
    # Step 3: Create mapping summary
    mapping = create_simple_mapping()
    
    print(f"\n=== DISCOVERY SUMMARY ===")
    print(f"✅ Confirmed Urgency: cf[10450] = 'High'")
    print(f"⏳ Components: cf[10449] (extraction needed)")
    print(f"⏳ Impact: cf[10451] (extraction needed)")
    print(f"❌ Company: Not found in tested range")
    print(f"📊 Additional fields found: {len(additional_fields)}")
    
    return {
        'additional_fields': additional_fields,
        'field_analysis': field_analysis,
        'mapping': mapping
    }

if __name__ == "__main__":
    main()