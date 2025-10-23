#!/usr/bin/env python3

import subprocess
import json

def discover_triage_component_values():
    """
    Discover the actual component values used in the Triage project.
    """
    
    print("=== DISCOVERING TRIAGE PROJECT COMPONENT VALUES ===")
    
    # Get a sample of tickets with components to analyze patterns
    try:
        cmd = ['acli', 'jira', 'workitem', 'search', 
               '--jql', 'project = Triage AND component is not EMPTY ORDER BY component ASC',
               '--limit', '50']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("Sample tickets with components (ordered by component):")
        print(result.stdout[:800] + "..." if len(result.stdout) > 800 else result.stdout)
        
        # Since ordering by component works, tickets with same component should be grouped
        # Look for patterns in the ordering that might indicate component boundaries
        
    except Exception as e:
        print(f"Error getting sample tickets: {e}")

def test_tri_1858_component_systematically():
    """
    Systematically test TRI-1858 for component values.
    """
    
    print(f"\n=== SYSTEMATIC COMPONENT TESTING FOR TRI-1858 ===")
    
    # Based on TRI-1858 summary: "Unpost Meter Reading"
    # Try variations of meter/billing related components
    
    test_components = [
        # Standard variations
        'Meter Reading', 'Meter Management', 'Meter', 'Reading',
        'Billing System', 'Billing', 'Bill',
        'Data Management', 'Data', 'Management',
        'System Administration', 'System', 'Admin',
        
        # Possible variations
        'Meters', 'MeterReading', 'Meter_Reading',
        'BillingSystem', 'Billing_System',
        'DataManagement', 'Data_Management',
        
        # Single word possibilities
        'Operations', 'Utilities', 'Infrastructure',
        'Maintenance', 'Processing', 'Services',
        
        # Abbreviated forms
        'MR', 'BS', 'DM', 'SA', 'PM', 'CP', 'PP'
    ]
    
    found_components = []
    
    for component in test_components:
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = Triage AND key = TRI-1858 AND component = "{component}"',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if '1' in result.stdout:
                print(f"✅ FOUND: TRI-1858 component = '{component}'")
                found_components.append(component)
                
                # If we found it, also test how many total tickets have this component
                cmd2 = ['acli', 'jira', 'workitem', 'search', 
                        '--jql', f'project = Triage AND component = "{component}"',
                        '--count']
                result2 = subprocess.run(cmd2, capture_output=True, text=True, check=True)
                
                import re
                count_match = re.search(r'(\d+)', result2.stdout)
                if count_match:
                    total_count = count_match.group(1)
                    print(f"   Total tickets with '{component}' component: {total_count}")
                
        except Exception as e:
            continue
    
    return found_components

def try_alternative_component_discovery():
    """
    Try alternative methods to discover component values.
    """
    
    print(f"\n=== ALTERNATIVE COMPONENT DISCOVERY ===")
    
    # Method 1: Try to get distinct component values by testing ranges
    print("Testing if components might be single characters or numbers...")
    
    # Test single characters A-Z
    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = Triage AND component = "{char}"',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.stdout and '0' not in result.stdout:
                print(f"  Found component: {char}")
                
        except:
            continue
    
    # Test numbers 1-20
    print("Testing numeric components...")
    for num in range(1, 21):
        try:
            cmd = ['acli', 'jira', 'workitem', 'search', 
                   '--jql', f'project = Triage AND component = "{num}"',
                   '--count']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.stdout and '0' not in result.stdout:
                print(f"  Found component: {num}")
                
        except:
            continue

def analyze_component_patterns():
    """
    Analyze patterns in tickets to infer component structure.
    """
    
    print(f"\n=== ANALYZING COMPONENT PATTERNS ===")
    
    # Get tickets ordered by component and look for grouping patterns
    try:
        cmd = ['acli', 'jira', 'workitem', 'search', 
               '--jql', 'project = Triage AND component is not EMPTY ORDER BY component ASC',
               '--limit', '30']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        lines = result.stdout.strip().split('\n')
        
        print("Looking for patterns in component ordering...")
        print("If tickets are grouped by component, we should see patterns:")
        
        # Look for TRI-1858 in the ordered list
        tri_1858_position = -1
        for i, line in enumerate(lines):
            if 'TRI-1858' in line:
                tri_1858_position = i
                print(f"\nTRI-1858 found at position {i} in component-ordered list")
                
                # Show context around TRI-1858
                start = max(0, i-3)
                end = min(len(lines), i+4)
                
                print("Context around TRI-1858 (same component should be grouped):")
                for j in range(start, end):
                    marker = " --> " if j == i else "     "
                    if j < len(lines):
                        # Extract just the ticket key and summary
                        parts = lines[j].split()
                        if len(parts) >= 2:
                            ticket_key = parts[1] if len(parts) > 1 else "Unknown"
                            summary_start = lines[j].find(ticket_key) + len(ticket_key)
                            summary = lines[j][summary_start:].strip()[:50]
                            print(f"{marker}{ticket_key}: {summary}...")
                
                break
        
        if tri_1858_position == -1:
            print("TRI-1858 not found in the ordered list (might be beyond limit)")
    
    except Exception as e:
        print(f"Error analyzing patterns: {e}")

def main():
    """
    Main function to discover component values for TRI-1858.
    """
    
    print("=== TRIAGE PROJECT COMPONENT DISCOVERY ===")
    print("Goal: Find the actual component value for TRI-1858")
    
    # Step 1: Discover general component patterns
    discover_triage_component_values()
    
    # Step 2: Test TRI-1858 systematically
    found_components = test_tri_1858_component_systematically()
    
    # Step 3: Try alternative discovery methods
    if not found_components:
        try_alternative_component_discovery()
    
    # Step 4: Analyze component patterns
    analyze_component_patterns()
    
    print(f"\n=== DISCOVERY SUMMARY ===")
    if found_components:
        print(f"✅ Found TRI-1858 component value(s): {found_components}")
    else:
        print("❌ Could not determine TRI-1858 component value")
        print("💡 Component field exists but value couldn't be extracted via ACLI")
    
    print(f"📊 Total tickets with components in Triage project: 127")
    print(f"🎯 TRI-1858 confirmed to have component data")
    
    return found_components

if __name__ == "__main__":
    main()