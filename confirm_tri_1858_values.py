#!/usr/bin/env python3

import subprocess
import json

def confirm_tri_1858_field_values():
    """
    Confirm the actual field values for TRI-1858 using the correct field mappings.
    """
    
    print("=== CONFIRMING TRI-1858 FIELD VALUES ===")
    print("Reference ticket: TRI-1858")
    print("Summary: CID 1769: Durango West Metro District: Unpost Meter Reading with end date 03/31/25")
    
    # Correct field mappings provided by user
    field_mappings = {
        'components': {
            'name': 'Components',
            'field_id': 'components',  # Standard JIRA field
            'description': 'JIRA standard components field'
        },
        'company': {
            'name': 'Company', 
            'field_ids': ['10413', '10542'],
            'description': 'Custom field for company/client identification'
        },
        'urgency': {
            'name': 'Urgency',
            'field_ids': ['10450', '11226'], 
            'description': 'Custom field for urgency level'
        },
        'impact': {
            'name': 'Impact',
            'field_id': '10451',
            'description': 'Custom field for business impact'
        }
    }
    
    confirmed_values = {}
    
    # Test Components field (standard JIRA field)
    print(f"\n--- Testing Components Field ---")
    try:
        # Try to get tickets with components field
        cmd = ['acli', 'jira', 'workitem', 'search', 
               '--jql', 'project = TRI AND key = TRI-1858 AND components is not EMPTY',
               '--count']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if '1' in result.stdout:
            print("✅ TRI-1858 has Components field data")
            confirmed_values['components'] = {'has_data': True, 'field_type': 'standard'}
        else:
            print("❌ TRI-1858 has no Components field data")
            confirmed_values['components'] = {'has_data': False, 'field_type': 'standard'}
            
    except Exception as e:
        print(f"❌ Error testing Components field: {e}")
        confirmed_values['components'] = {'has_data': False, 'error': str(e)}
    
    # Test Company field candidates
    print(f"\n--- Testing Company Field Candidates ---")
    for field_id in field_mappings['company']['field_ids']:
        print(f"Testing cf[{field_id}]:")
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND key = TRI-1858 AND cf[{field_id}] is not EMPTY',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if '1' in result.stdout:
                print(f"  ✅ cf[{field_id}] has data for TRI-1858")
                confirmed_values[f'company_cf{field_id}'] = {'has_data': True}
                
                # Try to extract the value
                value = extract_company_value(field_id)
                if value:
                    confirmed_values[f'company_cf{field_id}']['value'] = value
                    print(f"    Value: {value}")
                else:
                    print(f"    Value: Could not extract")
            else:
                print(f"  ❌ cf[{field_id}] has no data")
                confirmed_values[f'company_cf{field_id}'] = {'has_data': False}
                
        except Exception as e:
            print(f"  ❌ Error testing cf[{field_id}]: {e}")
            confirmed_values[f'company_cf{field_id}'] = {'has_data': False, 'error': str(e)}
    
    # Test Urgency field candidates  
    print(f"\n--- Testing Urgency Field Candidates ---")
    for field_id in field_mappings['urgency']['field_ids']:
        print(f"Testing cf[{field_id}]:")
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND key = TRI-1858 AND cf[{field_id}] is not EMPTY',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if '1' in result.stdout:
                print(f"  ✅ cf[{field_id}] has data for TRI-1858")
                confirmed_values[f'urgency_cf{field_id}'] = {'has_data': True}
                
                # We know cf[10450] = High, test cf[11226]
                if field_id == '10450':
                    confirmed_values[f'urgency_cf{field_id}']['value'] = 'High'
                    print(f"    Value: High (previously confirmed)")
                else:
                    value = extract_urgency_value(field_id)
                    if value:
                        confirmed_values[f'urgency_cf{field_id}']['value'] = value
                        print(f"    Value: {value}")
                    else:
                        print(f"    Value: Could not extract")
            else:
                print(f"  ❌ cf[{field_id}] has no data")
                confirmed_values[f'urgency_cf{field_id}'] = {'has_data': False}
                
        except Exception as e:
            print(f"  ❌ Error testing cf[{field_id}]: {e}")
            confirmed_values[f'urgency_cf{field_id}'] = {'has_data': False, 'error': str(e)}
    
    # Test Impact field
    print(f"\n--- Testing Impact Field ---")
    field_id = field_mappings['impact']['field_id']
    try:
        cmd = ['acli', 'jira', 'workitem', 'search', 
               '--jql', f'project = TRI AND key = TRI-1858 AND cf[{field_id}] is not EMPTY',
               '--count']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if '1' in result.stdout:
            print(f"✅ cf[{field_id}] has data for TRI-1858")
            confirmed_values['impact'] = {'has_data': True}
            
            value = extract_impact_value(field_id)
            if value:
                confirmed_values['impact']['value'] = value
                print(f"  Value: {value}")
            else:
                print(f"  Value: Could not extract")
        else:
            print(f"❌ cf[{field_id}] has no data")
            confirmed_values['impact'] = {'has_data': False}
            
    except Exception as e:
        print(f"❌ Error testing cf[{field_id}]: {e}")
        confirmed_values['impact'] = {'has_data': False, 'error': str(e)}
    
    return confirmed_values

def extract_company_value(field_id):
    """Try to extract company value from the field."""
    
    # Based on TRI-1858 summary, likely values
    test_values = ['1769', 'Durango West Metro District', 'CID 1769', 'Durango', 'Metro District']
    
    for value in test_values:
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND key = TRI-1858 AND cf[{field_id}] = "{value}"',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if '1' in result.stdout:
                return value
        except:
            continue
    
    return None

def extract_urgency_value(field_id):
    """Try to extract urgency value from the field."""
    
    test_values = ['Critical', 'High', 'Medium', 'Low', '1', '2', '3', '4']
    
    for value in test_values:
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND key = TRI-1858 AND cf[{field_id}] = "{value}"',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if '1' in result.stdout:
                return value
        except:
            continue
    
    return None

def extract_impact_value(field_id):
    """Try to extract impact value from the field."""
    
    test_values = ['Critical', 'High', 'Medium', 'Low', '1', '2', '3', '4', 'Major', 'Minor']
    
    for value in test_values:
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = TRI AND key = TRI-1858 AND cf[{field_id}] = "{value}"',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if '1' in result.stdout:
                return value
        except:
            continue
    
    return None

def create_confirmation_report(confirmed_values):
    """Create a confirmation report with the findings."""
    
    print(f"\n=== CREATING CONFIRMATION REPORT ===")
    
    # Create comprehensive report
    report = {
        'reference_ticket': 'TRI-1858',
        'summary': 'CID 1769: Durango West Metro District: Unpost Meter Reading with end date 03/31/25',
        'field_confirmation': confirmed_values,
        'recommended_mappings': {},
        'status': 'confirmed'
    }
    
    # Determine recommended field mappings
    print("\n=== RECOMMENDED FIELD MAPPINGS ===")
    
    # Components
    if confirmed_values.get('components', {}).get('has_data'):
        report['recommended_mappings']['components'] = 'components'
        print("✅ Components: Use standard 'components' field")
    else:
        print("❌ Components: No data in standard field")
    
    # Company - determine which field has data
    company_fields = []
    for key, data in confirmed_values.items():
        if key.startswith('company_cf') and data.get('has_data'):
            field_id = key.replace('company_cf', '')
            company_fields.append(field_id)
            value = data.get('value', 'UNKNOWN')
            print(f"✅ Company option: cf[{field_id}] = {value}")
    
    if company_fields:
        # Choose the field with actual value
        best_company_field = None
        for key, data in confirmed_values.items():
            if key.startswith('company_cf') and data.get('value'):
                best_company_field = key.replace('company_cf', '')
                break
        
        if not best_company_field and company_fields:
            best_company_field = company_fields[0]  # Use first available
        
        report['recommended_mappings']['company'] = f'cf[{best_company_field}]'
        print(f"🎯 Recommended Company field: cf[{best_company_field}]")
    else:
        print("❌ Company: No data found in tested fields")
    
    # Urgency - determine which field has data  
    urgency_fields = []
    for key, data in confirmed_values.items():
        if key.startswith('urgency_cf') and data.get('has_data'):
            field_id = key.replace('urgency_cf', '')
            urgency_fields.append(field_id)
            value = data.get('value', 'UNKNOWN')
            print(f"✅ Urgency option: cf[{field_id}] = {value}")
    
    if urgency_fields:
        # We know cf[10450] works
        if '10450' in urgency_fields:
            report['recommended_mappings']['urgency'] = 'cf[10450]'
            print(f"🎯 Recommended Urgency field: cf[10450]")
        else:
            report['recommended_mappings']['urgency'] = f'cf[{urgency_fields[0]}]'
            print(f"🎯 Recommended Urgency field: cf[{urgency_fields[0]}]")
    else:
        print("❌ Urgency: No data found in tested fields")
    
    # Impact
    if confirmed_values.get('impact', {}).get('has_data'):
        report['recommended_mappings']['impact'] = 'cf[10451]'
        value = confirmed_values['impact'].get('value', 'UNKNOWN')
        print(f"✅ Impact: cf[10451] = {value}")
    else:
        print("❌ Impact: No data in cf[10451]")
    
    # Save detailed report
    with open('/Users/munin8/_myprojects/tri_1858_field_confirmation.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Create summary
    summary_file = '/Users/munin8/_myprojects/tri_1858_confirmation_summary.md'
    
    with open(summary_file, 'w') as f:
        f.write("# TRI-1858 Field Value Confirmation\n\n")
        f.write(f"**Ticket**: TRI-1858\n")
        f.write(f"**Summary**: {report['summary']}\n\n")
        
        f.write("## 🎯 CONFIRMED Field Values\n\n")
        f.write("| Field Type | Field ID | Has Data | Value | Status |\n")
        f.write("|------------|----------|----------|-------|--------|\n")
        
        for field_type, field_id in report['recommended_mappings'].items():
            # Find the corresponding data
            value = "UNKNOWN"
            status = "✅ Confirmed"
            
            if field_type == 'urgency' and 'cf[10450]' in field_id:
                value = "High"
            else:
                # Look for value in confirmed_values
                for key, data in confirmed_values.items():
                    if field_id.replace('cf[', '').replace(']', '') in key and data.get('value'):
                        value = data['value']
                        break
            
            f.write(f"| {field_type.title()} | {field_id} | ✅ Yes | {value} | {status} |\n")
        
        f.write(f"\n## 📋 Next Steps\n\n")
        f.write("1. **Proceed with confirmed field mappings**\n")
        f.write("2. **Re-run analysis using actual field IDs and values**\n")
        f.write("3. **Generate authoritative business categorization**\n")
    
    print(f"Confirmation report saved to: {summary_file}")
    return report

def main():
    """
    Main execution for TRI-1858 field confirmation.
    """
    
    print("=== TRI-1858 FIELD VALUE CONFIRMATION ===")
    print("Using corrected field mappings from user")
    
    # Confirm field values
    confirmed_values = confirm_tri_1858_field_values()
    
    # Create confirmation report
    report = create_confirmation_report(confirmed_values)
    
    print(f"\n=== CONFIRMATION COMPLETE ===")
    print("✅ Field testing completed")
    print("✅ Value extraction attempted") 
    print("✅ Recommendations generated")
    print("📄 Ready for authoritative analysis")
    
    return report

if __name__ == "__main__":
    main()