#!/usr/bin/env python3

import subprocess
import csv
import re
from collections import Counter

def test_custom_field_for_categorical_data(field_id):
    """
    Test a specific custom field to see if it contains categorical/component-like data.
    """
    
    print(f"\n=== TESTING CUSTOM FIELD {field_id} ===")
    
    try:
        # Get a larger sample of tickets with this field
        cmd = ['acli', 'jira', 'workitem', 'search', 
               '--jql', f'project = TRI AND cf[{field_id}] is not EMPTY',
               '--limit', '50']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if not result.stdout.strip():
            print(f"No data found for cf[{field_id}]")
            return None
        
        # Parse the output to extract patterns
        lines = result.stdout.strip().split('\n')
        
        # Look for patterns that suggest this could be components
        patterns = {
            'billing_terms': 0,
            'payment_terms': 0,
            'portal_terms': 0,
            'system_terms': 0,
            'meter_terms': 0,
            'data_terms': 0
        }
        
        billing_keywords = ['billing', 'bill', 'invoice', 'charge', 'rate']
        payment_keywords = ['payment', 'autopay', 'check', 'card']
        portal_keywords = ['portal', 'customer', 'account', 'login']
        system_keywords = ['system', 'global', 'admin', 'config']
        meter_keywords = ['meter', 'reading', 'consumption', 'usage']
        data_keywords = ['data', 'export', 'import', 'file', 'report']
        
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in billing_keywords):
                patterns['billing_terms'] += 1
            if any(word in line_lower for word in payment_keywords):
                patterns['payment_terms'] += 1
            if any(word in line_lower for word in portal_keywords):
                patterns['portal_terms'] += 1
            if any(word in line_lower for word in system_keywords):
                patterns['system_terms'] += 1
            if any(word in line_lower for word in meter_keywords):
                patterns['meter_terms'] += 1
            if any(word in line_lower for word in data_keywords):
                patterns['data_terms'] += 1
        
        print(f"Pattern analysis for cf[{field_id}]:")
        total_lines = len([line for line in lines if line.strip() and not line.startswith(' Type')])
        
        for pattern, count in patterns.items():
            if count > 0:
                percentage = (count / total_lines) * 100 if total_lines > 0 else 0
                print(f"  {pattern}: {count} matches ({percentage:.1f}%)")
        
        # Calculate diversity score (higher = more likely to be components)
        diversity_score = len([count for count in patterns.values() if count > 0])
        print(f"  Diversity score: {diversity_score}/6 (higher = more likely components field)")
        
        return {
            'field_id': field_id,
            'total_tickets': total_lines,
            'patterns': patterns,
            'diversity_score': diversity_score,
            'sample_lines': lines[:10]
        }
        
    except Exception as e:
        print(f"Error testing cf[{field_id}]: {e}")
        return None

def try_to_extract_distinct_values(field_id):
    """
    Try to extract distinct values from a custom field to see if they look like components.
    """
    
    print(f"\n=== EXTRACTING DISTINCT VALUES FROM cf[{field_id}] ===")
    
    # Since we can't directly query for distinct values, we'll try different common component values
    potential_components = [
        'Billing', 'Payment Processing', 'Customer Portal', 'System Administration',
        'Meter Reading', 'Data Management', 'Account Management', 'Reports',
        'Integration', 'Autopay', 'Rate Management', 'Communication',
        'Service Requests', 'Technical Support', 'Configuration'
    ]
    
    found_components = []
    
    for component in potential_components:
        try:
            # Try to find tickets with this component value
            # We'll test both exact match and partial match strategies
            test_values = [component, component.replace(' ', ''), component.lower()]
            
            for test_value in test_values:
                cmd = ['acli', 'jira', 'workitem', 'search', 
                       '--jql', f'project = TRI AND cf[{field_id}] = "{test_value}"',
                       '--count']
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                if result.stdout.strip() and '0' not in result.stdout:
                    count_match = re.search(r'(\d+)', result.stdout)
                    if count_match:
                        count = int(count_match.group(1))
                        if count > 0:
                            found_components.append((test_value, count))
                            print(f"  Found '{test_value}': {count} tickets")
                            break
                            
        except Exception as e:
            continue
    
    if found_components:
        print(f"\nFound {len(found_components)} distinct component values in cf[{field_id}]!")
        return found_components
    else:
        print(f"No recognizable component values found in cf[{field_id}]")
        return []

def comprehensive_field_analysis():
    """
    Systematically analyze all candidate custom fields.
    """
    
    print("=== COMPREHENSIVE CUSTOM FIELD ANALYSIS ===")
    
    # Test the most promising fields
    candidate_fields = ['10449', '10451', '10452', '10453']
    
    results = {}
    
    for field_id in candidate_fields:
        print(f"\n{'='*60}")
        print(f"ANALYZING CUSTOM FIELD {field_id}")
        print(f"{'='*60}")
        
        # Test for categorical patterns
        pattern_result = test_custom_field_for_categorical_data(field_id)
        
        # Try to extract distinct values
        component_result = try_to_extract_distinct_values(field_id)
        
        results[field_id] = {
            'patterns': pattern_result,
            'components': component_result
        }
    
    return results

def create_recommendation_based_on_analysis(results):
    """
    Create recommendations based on the analysis results.
    """
    
    print(f"\n{'='*60}")
    print("ANALYSIS SUMMARY AND RECOMMENDATIONS")
    print(f"{'='*60}")
    
    for field_id, data in results.items():
        print(f"\n--- Custom Field {field_id} ---")
        
        if data['patterns']:
            patterns = data['patterns']
            print(f"Total tickets analyzed: {patterns['total_tickets']}")
            print(f"Diversity score: {patterns['diversity_score']}/6")
            
            if patterns['diversity_score'] >= 4:
                print(f"✅ HIGH LIKELIHOOD of being components field")
            elif patterns['diversity_score'] >= 2:
                print(f"🟡 MODERATE LIKELIHOOD of being components field")
            else:
                print(f"❌ LOW LIKELIHOOD of being components field")
        
        if data['components']:
            print(f"Found {len(data['components'])} distinct component-like values")
            print(f"✅ STRONG INDICATION this is the components field!")
        else:
            print(f"No distinct component values identified")
    
    # Find the best candidate
    best_field = None
    best_score = 0
    
    for field_id, data in results.items():
        score = 0
        if data['patterns'] and data['patterns']['diversity_score']:
            score += data['patterns']['diversity_score']
        if data['components']:
            score += len(data['components']) * 2
        
        if score > best_score:
            best_score = score
            best_field = field_id
    
    print(f"\n🎯 RECOMMENDATION:")
    if best_field:
        print(f"Custom field cf[{best_field}] is most likely the components field")
        print(f"Confidence score: {best_score}")
    else:
        print("Could not identify a clear components field candidate")
        print("The components field may not be accessible through ACLI or may not exist")
    
    return best_field

if __name__ == "__main__":
    results = comprehensive_field_analysis()
    recommended_field = create_recommendation_based_on_analysis(results)
    
    print(f"\n=== NEXT STEPS ===")
    if recommended_field:
        print(f"1. Use cf[{recommended_field}] as the components field for analysis")
        print(f"2. Create new category analysis based on cf[{recommended_field}] values")
        print(f"3. Generate updated CSV exports with proper component categorization")
    else:
        print("1. Manual investigation of JIRA configuration may be needed")
        print("2. Components field may not be accessible via API")
        print("3. Consider using existing refined categorization as alternative")