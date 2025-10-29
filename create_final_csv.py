#!/usr/bin/env python3
"""
Final TriQ CSV Export - All 631 tickets with accurate parsing
"""

import subprocess
import csv
import re

def get_urgency_mapping():
    """Get urgency mapping for all tickets"""
    urgency_map = {}
    for urgency in ['Critical', 'High', 'Medium', 'Low']:
        try:
            result = subprocess.run([
                'acli', 'jira', 'workitem', 'search', 
                '--jql', f'project = TRI AND created >= -365d AND cf[10450] = "{urgency}"',
                '--limit', '200'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'TRI-' in line:
                        # Extract ticket key
                        match = re.search(r'(TRI-\d+)', line)
                        if match:
                            ticket_key = match.group(1)
                            urgency_map[ticket_key] = urgency
        except Exception as e:
            print(f"Error getting {urgency} tickets: {e}")
    return urgency_map

def extract_cid(summary):
    """Extract CID from summary"""
    cid_match = re.search(r'CID[:\s-]*(\d+)', summary, re.IGNORECASE)
    return cid_match.group(1) if cid_match else ''

def categorize_issue(summary):
    """Categorize issue type"""
    summary_lower = summary.lower()
    
    if any(word in summary_lower for word in ['autopay', 'auto pay', 'automatic payment']):
        return 'Autopay System'
    elif any(word in summary_lower for word in ['payment', 'e-check', 'echeck', 'pay']):
        return 'Payment Processing'
    elif any(word in summary_lower for word in ['bill', 'billing', 'invoice', 'charge', 'statement']):
        return 'Billing System'
    elif any(word in summary_lower for word in ['integration', 'sync', 'fortress', 'watersmart', 'import', 'export']):
        return 'Integration'
    elif any(word in summary_lower for word in ['portal', 'login', 'password', 'user access']):
        return 'Customer Portal'
    elif any(word in summary_lower for word in ['meter', 'reading', 'consumption']):
        return 'Meter Management'
    elif any(word in summary_lower for word in ['enhance', 'functionality', 'feature', 'improve']):
        return 'Enhancement'
    elif any(word in summary_lower for word in ['data', 'file format', 'export', 'import']):
        return 'Data Management'
    elif any(word in summary_lower for word in ['global', 'system', 'performance', 'slowness']):
        return 'System Performance'
    else:
        return 'Other'

def calculate_triq_score(summary, assignee, status, urgency):
    """Calculate estimated TriQ score"""
    score = 5.0
    
    # Summary quality
    if 'CID' in summary and ':' in summary:
        score += 2.0
    elif 'CID' in summary:
        score += 1.0
    
    if len(summary) > 50:
        score += 1.0
    elif len(summary) < 20:
        score -= 1.0
    
    # Assignment quality
    if assignee and assignee != '':
        score += 1.0
    else:
        score -= 1.0
    
    # Status appropriateness
    if status in ['Resolved', 'Closed']:
        score += 0.5
    elif status == 'In Progress' and assignee:
        score += 0.3
    
    # Urgency handling
    if urgency == 'Critical' and not assignee:
        score -= 2.0
    elif urgency == 'High' and not assignee:
        score -= 1.0
    
    return round(min(10.0, max(1.0, score)), 1)

def assess_quality_issues(summary, assignee, status, urgency):
    """Assess quality issues"""
    issues = []
    
    if not assignee or assignee.strip() == '':
        if urgency == 'Critical':
            issues.append("UNASSIGNED CRITICAL - SLA BREACH RISK")
        elif urgency == 'High':
            issues.append("UNASSIGNED HIGH URGENCY")
        else:
            issues.append("UNASSIGNED")
    
    if len(summary) < 20:
        issues.append("VAGUE SUMMARY")
    
    if urgency in ['Critical', 'High'] and len(summary) < 30:
        issues.append(f"{urgency.upper()} URGENCY LACKS DETAIL")
    
    if status == "Waiting for customer" and len(summary) < 40:
        issues.append("WAITING WITHOUT PROPER INVESTIGATION")
    
    return "; ".join(issues) if issues else "Standard quality"

def determine_action_required(triq_score, status, assignee, urgency, quality_issues):
    """Determine required action"""
    if "SLA BREACH RISK" in quality_issues:
        return "URGENT: ASSIGN IMMEDIATELY"
    elif "UNASSIGNED HIGH URGENCY" in quality_issues:
        return "URGENT: ASSIGN SPECIALIST"
    elif triq_score < 4.0:
        return "REQUEST REVISION"
    elif "UNASSIGNED" in quality_issues:
        return "ASSIGN TO SPECIALIST"
    elif triq_score >= 8.0:
        return "USE AS TEMPLATE"
    elif status in ['Resolved', 'Closed']:
        return "RESOLVED"
    elif status == 'Pending' and 'Enhancement' in quality_issues:
        return "ROUTE TO PRODUCT MGMT"
    else:
        return "STANDARD PROCESSING"

def main():
    print("Creating comprehensive CSV export for all 631 TRI tickets...")
    
    # Get urgency mapping
    print("Getting urgency mapping...")
    urgency_map = get_urgency_mapping()
    print(f"Mapped urgency for {len(urgency_map)} tickets")
    
    # Get all tickets
    print("Getting all ticket data...")
    try:
        result = subprocess.run([
            'acli', 'jira', 'workitem', 'search', 
            '--jql', 'project = TRI AND created >= -365d',
            '--limit', '631'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return
        
        lines = result.stdout.strip().split('\n')
        
        # Create CSV
        with open('/Users/munin8/_myprojects/tri-all-tickets-final.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Ticket_Key', 'Summary', 'Status', 'Assignee', 'Urgency', 'Priority', 
                'JIRA_URL', 'TriQ_Score', 'Quality_Issues', 'Client_CID', 
                'Issue_Category', 'Action_Required'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            processed = 0
            for line in lines:
                if '[System] Service request' in line and 'TRI-' in line:
                    try:
                        # Parse the line more carefully
                        parts = line.strip().split()
                        
                        # Find TRI- ticket key
                        ticket_key = None
                        for part in parts:
                            if 'TRI-' in part:
                                ticket_key = part
                                break
                        
                        if not ticket_key:
                            continue
                        
                        # Extract assignee (next significant part after ticket key)
                        ticket_idx = parts.index(ticket_key)
                        assignee = ''
                        if ticket_idx + 1 < len(parts) and '@' in parts[ticket_idx + 1]:
                            assignee = parts[ticket_idx + 1].replace('…', '@munibilling.com')
                        
                        # Find status (look for known status values)
                        status = 'Unknown'
                        status_keywords = ['Resolved', 'Closed', 'Progress', 'Pending', 'Canceled', 'support', 'customer']
                        for part in parts:
                            if any(keyword in part for keyword in status_keywords):
                                if 'Progress' in part:
                                    status = 'In Progress'
                                elif 'support' in part:
                                    status = 'Waiting for support'
                                elif 'customer' in part:
                                    status = 'Waiting for customer'
                                else:
                                    status = part
                                break
                        
                        # Extract summary (everything after the last status/assignee info)
                        summary_parts = []
                        collecting_summary = False
                        for part in parts:
                            if collecting_summary:
                                summary_parts.append(part)
                            elif part in ['Resolved', 'Closed', 'Pending', 'Canceled'] or 'Progress' in part or 'support' in part or 'customer' in part:
                                collecting_summary = True
                        
                        summary = ' '.join(summary_parts).replace('…', '...').strip()
                        if not summary:
                            summary = f"Issue {ticket_key}"
                        
                        # Get data
                        urgency = urgency_map.get(ticket_key, 'Unknown')
                        cid = extract_cid(summary)
                        issue_category = categorize_issue(summary)
                        triq_score = calculate_triq_score(summary, assignee, status, urgency)
                        quality_issues = assess_quality_issues(summary, assignee, status, urgency)
                        action_required = determine_action_required(triq_score, status, assignee, urgency, quality_issues)
                        
                        writer.writerow({
                            'Ticket_Key': ticket_key,
                            'Summary': summary,
                            'Status': status,
                            'Assignee': assignee,
                            'Urgency': urgency,
                            'Priority': 'Normal',
                            'JIRA_URL': f'https://jiramb.atlassian.net/browse/{ticket_key}',
                            'TriQ_Score': triq_score,
                            'Quality_Issues': quality_issues,
                            'Client_CID': cid,
                            'Issue_Category': issue_category,
                            'Action_Required': action_required
                        })
                        
                        processed += 1
                        if processed % 50 == 0:
                            print(f"Processed {processed} tickets...")
                    
                    except Exception as e:
                        print(f"Error processing line: {str(e)}")
                        continue
            
            print(f"Successfully exported {processed} tickets to CSV")
            
        # Create summary statistics
        print("Creating summary statistics...")
        with open('/Users/munin8/_myprojects/tri-tickets-summary.txt', 'w') as f:
            f.write(f"TRI Tickets Summary (Past Year)\n")
            f.write(f"================================\n\n")
            f.write(f"Total Tickets Processed: {processed}\n")
            f.write(f"Urgency Distribution:\n")
            urgency_counts = {}
            for urgency in urgency_map.values():
                urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
            
            for urgency, count in sorted(urgency_counts.items()):
                percentage = (count / len(urgency_map)) * 100 if urgency_map else 0
                f.write(f"  {urgency}: {count} ({percentage:.1f}%)\n")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()