#!/usr/bin/env python3

import subprocess
import json
import re

def test_company_field_candidates():
    """
    Test the newly discovered fields as Company field candidates.
    """
    
    print("=== TESTING COMPANY FIELD CANDIDATES ===")
    
    # Test new fields found: cf[10413], cf[10432], cf[10433]
    company_candidates = [10413, 10432, 10433]
    
    # Test with CID 1769 from TRI-1858
    for field_id in company_candidates:
        print(f"\n--- Testing cf[{field_id}] as Company field ---")
        
        # Test if this field contains client/company identifiers
        test_patterns = ['1769', 'Durango', 'District', 'Metro']
        
        for pattern in test_patterns:
            try:
                cmd = ['acli', 'jira', 'workitem', 'search', 
                       '--jql', f'project = TRI AND cf[{field_id}] = "{pattern}"',
                       '--count']
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                count_match = re.search(r'(\d+)', result.stdout)
                if count_match and int(count_match.group(1)) > 0:
                    print(f"  ✅ Found '{pattern}': {count_match.group(1)} tickets")
                    
            except Exception as e:
                continue
        
        # Get total tickets with this field
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND cf[{field_id}] is not EMPTY',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            count_match = re.search(r'(\d+)', result.stdout)
            if count_match:
                total = int(count_match.group(1))
                print(f"  Total tickets with cf[{field_id}]: {total}")
                
        except Exception as e:
            print(f"  Error getting total count: {e}")

def try_reverse_engineering_approach():
    """
    Try to reverse engineer field values by looking at export patterns.
    """
    
    print(f"\n=== REVERSE ENGINEERING FIELD VALUES ===")
    
    # Export TRI-1858 data and try to find patterns
    try:
        cmd = ['acli', 'jira', 'workitem', 'search', 
               '--jql', 'project = TRI AND key = TRI-1858',
               '--csv']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("TRI-1858 CSV export:")
        print(result.stdout)
        
        # Look for any additional data that might indicate field values
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            headers = lines[0].split(',')
            values = lines[1].split(',')
            
            print(f"\nField mapping:")
            for i, (header, value) in enumerate(zip(headers, values)):
                if value and value != 'TRI-1858':  # Skip empty and key
                    print(f"  {header}: {value}")
    
    except Exception as e:
        print(f"Error in reverse engineering: {e}")

def test_components_values_systematically():
    """
    Systematically test for Components field values.
    """
    
    print(f"\n=== SYSTEMATIC COMPONENTS VALUE TESTING ===")
    
    # Based on TRI-1858 summary: "Unpost Meter Reading"
    # This strongly suggests Meter Reading component
    
    meter_related_components = [
        'Meter Reading', 'Meter Management', 'Meters', 'Reading',
        'Meter_Reading', 'MeterReading', 'METER_READING'
    ]
    
    for component in meter_related_components:
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND key = TRI-1858 AND cf[10449] = "{component}"',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if '1' in result.stdout:
                print(f"  ✅ Components field value: {component}")
                return component
                
        except Exception as e:
            continue
    
    print("  ❌ Could not determine Components value")
    return None

def test_impact_values_systematically():
    """
    Systematically test for Impact field values.
    """
    
    print(f"\n=== SYSTEMATIC IMPACT VALUE TESTING ===")
    
    # Since Urgency is High, Impact might correlate
    impact_values = [
        'High', 'Medium', 'Low', 'Critical',
        '1', '2', '3', '4', '5',
        'Major', 'Minor', 'Significant'
    ]
    
    for impact in impact_values:
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND key = TRI-1858 AND cf[10451] = "{impact}"',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if '1' in result.stdout:
                print(f"  ✅ Impact field value: {impact}")
                return impact
                
        except Exception as e:
            continue
    
    print("  ❌ Could not determine Impact value")
    return None

def create_updated_field_mapping():
    """
    Create updated field mapping with all discovered information.
    """
    
    print(f"\n=== CREATING UPDATED FIELD MAPPING ===")
    
    # Test for Components and Impact values
    components_value = test_components_values_systematically()
    impact_value = test_impact_values_systematically()
    
    # Create comprehensive mapping
    field_mapping = {
        'reference_ticket': 'TRI-1858',
        'confirmed_fields': {
            'cf[10449]': {
                'name': 'Components',
                'value': components_value if components_value else 'UNKNOWN',
                'confidence': 'High' if components_value else 'Low'
            },
            'cf[10450]': {
                'name': 'Urgency', 
                'value': 'High',
                'confidence': 'High'
            },
            'cf[10451]': {
                'name': 'Impact',
                'value': impact_value if impact_value else 'UNKNOWN', 
                'confidence': 'High' if impact_value else 'Low'
            }
        },
        'additional_fields': {
            'cf[10413]': {'status': 'potential_company', 'investigation': 'needed'},
            'cf[10432]': {'status': 'potential_company', 'investigation': 'needed'},
            'cf[10433]': {'status': 'potential_company', 'investigation': 'needed'}
        },
        'status': {
            'components_identified': bool(components_value),
            'impact_identified': bool(impact_value),
            'urgency_confirmed': True,
            'company_field_found': False
        }
    }
    
    # Save to file
    with open('/Users/munin8/_myprojects/tri_final_field_mapping.json', 'w') as f:
        json.dump(field_mapping, f, indent=2)
    
    # Create readable summary
    summary_file = '/Users/munin8/_myprojects/tri_field_mapping_final.md'
    
    with open(summary_file, 'w') as f:
        f.write("# TRI Custom Fields - Final Mapping\n\n")
        f.write(f"**Reference Ticket**: TRI-1858\n\n")
        
        f.write("## ✅ Confirmed Field Values for TRI-1858\n\n")
        f.write("| Field ID | Field Name | Value | Confidence |\n")
        f.write("|----------|------------|-------|------------|\n")
        
        for field_id, data in field_mapping['confirmed_fields'].items():
            confidence_emoji = "✅" if data['confidence'] == 'High' else "⚠️"
            f.write(f"| {field_id} | {data['name']} | {data['value']} | {confidence_emoji} {data['confidence']} |\n")
        
        f.write(f"\n## 🔍 Additional Fields Found\n\n")
        f.write("| Field ID | Status | Notes |\n")
        f.write("|----------|--------|-------|\n")
        
        for field_id, data in field_mapping['additional_fields'].items():
            f.write(f"| {field_id} | {data['status']} | {data['investigation']} |\n")
        
        f.write(f"\n## 📊 Analysis Status\n\n")
        status = field_mapping['status']
        f.write(f"- **Components**: {'✅ Identified' if status['components_identified'] else '❌ Not found'}\n")
        f.write(f"- **Impact**: {'✅ Identified' if status['impact_identified'] else '❌ Not found'}\n")
        f.write(f"- **Urgency**: {'✅ Confirmed' if status['urgency_confirmed'] else '❌ Not confirmed'}\n")
        f.write(f"- **Company**: {'✅ Found' if status['company_field_found'] else '❌ Still searching'}\n")
    
    print(f"Final mapping saved to: {summary_file}")
    return field_mapping

def main():
    """
    Main execution for alternative field value extraction.
    """
    
    print("=== ALTERNATIVE FIELD VALUE EXTRACTION ===")
    
    # Step 1: Test company field candidates
    test_company_field_candidates()
    
    # Step 2: Try reverse engineering
    try_reverse_engineering_approach()
    
    # Step 3: Create updated mapping
    final_mapping = create_updated_field_mapping()
    
    print(f"\n=== EXTRACTION RESULTS ===")
    confirmed = final_mapping['confirmed_fields']
    
    for field_id, data in confirmed.items():
        status = "✅" if data['value'] != 'UNKNOWN' else "❌"
        print(f"{status} {field_id} ({data['name']}): {data['value']}")
    
    return final_mapping

if __name__ == "__main__":
    main()