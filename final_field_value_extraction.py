#!/usr/bin/env python3

import subprocess
import json

def analyze_field_patterns_across_tickets():
    """
    Analyze patterns across multiple tickets to understand field contents.
    """
    
    print("=== ANALYZING FIELD PATTERNS ACROSS TICKETS ===")
    
    # Get multiple tickets that have these custom fields
    try:
        cmd = ['acli', 'jira', 'workitem', 'search', 
               '--jql', 'project = TRI AND cf[10449] is not EMPTY',
               '--limit', '20']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("Sample tickets with cf[10449] (Components):")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        
        # Look for patterns in summaries that might indicate component types
        lines = result.stdout.split('\n')
        patterns = {
            'billing': 0, 'payment': 0, 'meter': 0, 'portal': 0, 
            'data': 0, 'system': 0, 'account': 0, 'report': 0
        }
        
        for line in lines:
            line_lower = line.lower()
            for pattern in patterns.keys():
                if pattern in line_lower:
                    patterns[pattern] += 1
        
        print("\nPattern analysis:")
        for pattern, count in patterns.items():
            if count > 0:
                print(f"  {pattern}: {count} matches")
                
    except Exception as e:
        print(f"Error analyzing patterns: {e}")

def test_probable_values_based_on_context():
    """
    Test probable values based on business context and ticket content.
    """
    
    print(f"\n=== TESTING PROBABLE VALUES BASED ON CONTEXT ===")
    
    # For TRI-1858: "CID 1769: Durango West Metro District: Unpost Meter Reading"
    # Most likely:
    # - Components: Something related to meter reading
    # - Impact: Based on urgency being High, likely Medium or High
    # - Company: Likely "1769" or "Durango West Metro District"
    
    probable_tests = [
        {
            'field': 'cf[10449]',
            'name': 'Components',
            'values': ['Meter Management', 'Meter Reading', 'Billing System', 'Data Management']
        },
        {
            'field': 'cf[10451]', 
            'name': 'Impact',
            'values': ['High', 'Medium', '2', '3']
        },
        {
            'field': 'cf[10413]',
            'name': 'Company (candidate 1)',
            'values': ['1769', 'Durango West Metro District', 'CID 1769']
        },
        {
            'field': 'cf[10432]',
            'name': 'Company (candidate 2)', 
            'values': ['1769', 'Durango West Metro District', 'CID 1769']
        },
        {
            'field': 'cf[10433]',
            'name': 'Company (candidate 3)',
            'values': ['1769', 'Durango West Metro District', 'CID 1769']
        }
    ]
    
    results = {}
    
    for test in probable_tests:
        field = test['field']
        name = test['name']
        
        print(f"\n--- Testing {name} ({field}) ---")
        
        found_value = None
        for value in test['values']:
            try:
                cmd = ['acli', 'jira', 'workitem', 'search', 
                       '--jql', f'project = TRI AND key = TRI-1858 AND {field} = "{value}"',
                       '--count']
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                if '1' in result.stdout:
                    print(f"  ✅ Found value: {value}")
                    found_value = value
                    break
                    
            except Exception as e:
                continue
        
        if not found_value:
            print(f"  ❌ No value found from test set")
        
        results[field] = {
            'name': name,
            'value': found_value,
            'tested_values': test['values']
        }
    
    return results

def create_business_ready_analysis():
    """
    Create a business-ready analysis with what we can confirm.
    """
    
    print(f"\n=== CREATING BUSINESS-READY ANALYSIS ===")
    
    # Test the probable values
    field_results = test_probable_values_based_on_context()
    
    # Create definitive mapping
    definitive_mapping = {
        'reference_ticket': 'TRI-1858',
        'summary': 'CID 1769: Durango West Metro District: Unpost Meter Reading with end date 03/31/25',
        'confirmed_fields': {},
        'probable_fields': {},
        'status': 'partial_identification'
    }
    
    # Process results
    for field_id, data in field_results.items():
        if data['value']:
            definitive_mapping['confirmed_fields'][field_id] = {
                'name': data['name'],
                'value': data['value'],
                'confidence': 'High'
            }
        else:
            definitive_mapping['probable_fields'][field_id] = {
                'name': data['name'],
                'likely_values': data['tested_values'],
                'confidence': 'Low'
            }
    
    # Save comprehensive results
    with open('/Users/munin8/_myprojects/tri_definitive_field_analysis.json', 'w') as f:
        json.dump(definitive_mapping, f, indent=2)
    
    # Create executive summary
    summary_file = '/Users/munin8/_myprojects/tri_field_identification_executive_summary.md'
    
    with open(summary_file, 'w') as f:
        f.write("# TRI Custom Fields - Executive Summary\n\n")
        f.write(f"**Reference Ticket**: TRI-1858\n")
        f.write(f"**Ticket Summary**: {definitive_mapping['summary']}\n\n")
        
        f.write("## 🎯 CONFIRMED Field Values\n\n")
        
        if definitive_mapping['confirmed_fields']:
            f.write("| Field ID | Field Name | Value | Business Impact |\n")
            f.write("|----------|------------|-------|----------------|\n")
            
            for field_id, data in definitive_mapping['confirmed_fields'].items():
                impact = get_business_impact(data['name'], data['value'])
                f.write(f"| {field_id} | {data['name']} | {data['value']} | {impact} |\n")
        else:
            f.write("No field values definitively confirmed through automated extraction.\n")
        
        f.write(f"\n## ⚠️ IDENTIFICATION CHALLENGES\n\n")
        f.write("### Known Issues:\n")
        f.write("1. **ACLI Limitations**: Cannot extract actual custom field values directly\n")
        f.write("2. **API Restrictions**: Standard JIRA API access limited for custom fields\n")
        f.write("3. **Field Value Format**: Unknown format/structure of field values\n\n")
        
        f.write("### What We DO Know:\n")
        f.write("- **cf[10449]** = Components field (high confidence)\n")
        f.write("- **cf[10450]** = Urgency field = 'High' (confirmed)\n") 
        f.write("- **cf[10451]** = Impact field (high confidence)\n")
        f.write("- **cf[10413], cf[10432], cf[10433]** = Potential Company fields\n\n")
        
        f.write("## 🚀 RECOMMENDED NEXT STEPS\n\n")
        f.write("### Option 1: Manual Verification\n")
        f.write("- Open TRI-1858 in JIRA web interface\n")
        f.write("- Manually inspect Components, Impact, and Company field values\n")
        f.write("- Confirm field mappings against business requirements\n\n")
        
        f.write("### Option 2: Proceed with Available Data\n")
        f.write("- Use cf[10450] (Urgency) as confirmed field\n")
        f.write("- Apply business logic based on ticket content\n")
        f.write("- Generate analysis with available categorization\n\n")
        
        f.write("### Option 3: Alternative Analysis Approach\n")
        f.write("- Use our refined categorization from previous analysis\n")
        f.write("- Combine with confirmed Urgency field data\n")
        f.write("- Create hybrid analysis approach\n")
    
    print(f"Executive summary saved to: {summary_file}")
    return definitive_mapping

def get_business_impact(field_name, value):
    """Get business impact description for field values."""
    
    impacts = {
        ('Urgency', 'High'): 'Critical business priority, immediate attention required',
        ('Components', 'Meter Reading'): 'Core utility operations, affects billing accuracy',
        ('Components', 'Billing System'): 'Revenue cycle operations, customer billing',
        ('Impact', 'High'): 'Significant business disruption potential',
        ('Impact', 'Medium'): 'Moderate business impact, manageable disruption'
    }
    
    return impacts.get((field_name, value), 'Business impact assessment needed')

def main():
    """
    Final attempt at comprehensive field value extraction.
    """
    
    print("=== FINAL COMPREHENSIVE FIELD VALUE EXTRACTION ===")
    print("Target: Extract actual values for Components, Impact, Urgency, Company")
    print("Reference: TRI-1858")
    
    # Step 1: Analyze patterns across multiple tickets
    analyze_field_patterns_across_tickets()
    
    # Step 2: Create business-ready analysis
    final_results = create_business_ready_analysis()
    
    print(f"\n=== FINAL EXTRACTION SUMMARY ===")
    
    confirmed = final_results.get('confirmed_fields', {})
    probable = final_results.get('probable_fields', {})
    
    print(f"✅ Confirmed fields: {len(confirmed)}")
    for field_id, data in confirmed.items():
        print(f"   {field_id} ({data['name']}): {data['value']}")
    
    print(f"⚠️ Probable fields: {len(probable)}")
    for field_id, data in probable.items():
        print(f"   {field_id} ({data['name']}): Investigation needed")
    
    print(f"\n📋 Next step: Manual verification recommended")
    
    return final_results

if __name__ == "__main__":
    main()