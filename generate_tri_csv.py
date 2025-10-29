#!/usr/bin/env python3
"""
TriQ CSV Export Generator
Processes all 631 TRI tickets and generates comprehensive CSV with TriQ scores
"""

import subprocess
import csv
import re
import json
from datetime import datetime

def extract_cid(summary):
    """Extract CID from ticket summary"""
    cid_match = re.search(r'CID[:\s-]*(\d+)', summary, re.IGNORECASE)
    return cid_match.group(1) if cid_match else 'N/A'

def categorize_issue(summary, description=""):
    """Categorize the issue type based on summary and description"""
    summary_lower = summary.lower()
    desc_lower = description.lower()
    text = f"{summary_lower} {desc_lower}"
    
    if any(word in text for word in ['payment', 'autopay', 'e-check', 'billing', 'bill', 'charge', 'invoice']):
        if any(word in text for word in ['autopay', 'auto pay', 'automatic']):
            return 'Autopay System'
        elif any(word in text for word in ['payment', 'e-check', 'check']):
            return 'Payment Processing'
        else:
            return 'Billing System'
    elif any(word in text for word in ['integration', 'sync', 'fortress', 'watersmart', 'import', 'export']):
        return 'Integration'
    elif any(word in text for word in ['portal', 'login', 'password', 'user', 'customer portal']):
        return 'Customer Portal'
    elif any(word in text for word in ['meter', 'reading', 'consumption']):
        return 'Meter Management'
    elif any(word in text for word in ['enhancement', 'improve', 'functionality', 'feature']):
        return 'Enhancement'
    elif any(word in text for word in ['data', 'export', 'import', 'file', 'format']):
        return 'Data Management'
    elif any(word in text for word in ['global', 'system', 'performance', 'slowness']):
        return 'System Performance'
    else:
        return 'Other'

def calculate_triq_score(summary, has_description, status, assignee):
    """Calculate TriQ score based on available information"""
    score = 5.0  # Base score
    
    # Summary quality (25% weight)
    if 'CID' in summary and len(summary) > 20:
        score += 1.5
    elif len(summary) > 10:
        score += 0.5
    
    # Description quality (35% weight) - estimated
    if has_description:
        score += 2.0
    else:
        score -= 1.0
    
    # Assignment and status (metadata quality)
    if assignee and assignee != 'UNASSIGNED':
        score += 0.5
    else:
        score -= 0.5
    
    # Status appropriateness
    if status in ['Resolved', 'Closed']:
        score += 0.5
    elif status in ['In Progress'] and assignee:
        score += 0.3
    
    return min(10.0, max(1.0, round(score, 1)))

def assess_quality_issues(summary, has_description, status, assignee, urgency):
    """Assess quality issues for the ticket"""
    issues = []
    
    if not has_description:
        issues.append("NO DESCRIPTION")
    
    if not assignee or assignee == 'UNASSIGNED':
        if urgency == 'Critical':
            issues.append("UNASSIGNED CRITICAL - SLA BREACH RISK")
        elif urgency == 'High':
            issues.append("UNASSIGNED HIGH URGENCY")
        else:
            issues.append("UNASSIGNED")
    
    if len(summary) < 10:
        issues.append("VAGUE SUMMARY")
    
    if status == "Waiting for customer" and not has_description:
        issues.append("WAITING WITHOUT INVESTIGATION")
    
    if urgency in ['Critical', 'High'] and not has_description:
        issues.append(f"{urgency.upper()} URGENCY LACKS DETAIL")
    
    return "; ".join(issues) if issues else "Standard quality"

def determine_action_required(triq_score, status, assignee, urgency, quality_issues):
    """Determine action required based on assessment"""
    if "SLA BREACH RISK" in quality_issues:
        return "URGENT: ASSIGN + DESCRIBE"
    elif triq_score < 5.0:
        return "REQUEST REVISION"
    elif "UNASSIGNED" in quality_issues:
        return "ASSIGN SPECIALIST"
    elif status == "Pending" and "Enhancement" in quality_issues:
        return "ROUTE TO PRODUCT MGMT"
    elif triq_score >= 8.5:
        return "USE AS TEMPLATE"
    elif status in ['Resolved', 'Closed']:
        return "RESOLVED"
    else:
        return "STANDARD PROCESSING"

# Generate the comprehensive CSV
def generate_csv():
    print("Generating comprehensive TRI tickets CSV...")
    
    # Get urgency data for all tickets
    urgency_map = {}
    for urgency in ['Critical', 'High', 'Medium', 'Low']:
        try:
            result = subprocess.run([
                'acli', 'jira', 'workitem', 'search', 
                '--jql', f'project = TRI AND created >= -365d AND cf[10450] = "{urgency}"'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[2:]:  # Skip header lines
                    if line.strip() and 'TRI-' in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            ticket_key = parts[3]  # Ticket key position
                            urgency_map[ticket_key] = urgency
        except Exception as e:
            print(f"Error getting {urgency} tickets: {e}")
    
    # Get all tickets
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
        with open('/Users/munin8/_myprojects/tri-all-tickets-comprehensive.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Ticket_Key', 'Summary', 'Status', 'Assignee', 'Urgency', 'Priority', 
                'JIRA_URL', 'TriQ_Score', 'Quality_Issues', 'Client_CID', 
                'Issue_Category', 'Action_Required', 'Created_Date'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            processed = 0
            for line in lines[2:]:  # Skip header lines
                if line.strip() and 'TRI-' in line:
                    try:
                        parts = line.split()
                        if len(parts) >= 6:
                            ticket_key = parts[3]
                            assignee = parts[4] if parts[4] != '…' else 'UNASSIGNED'
                            if assignee.endswith('…'):
                                assignee = assignee[:-1] + '@munibilling.com'
                            status = parts[6]
                            
                            # Get summary (everything after status)
                            summary_start = line.find(status) + len(status)
                            summary = line[summary_start:].strip()
                            if summary.endswith('…'):
                                summary = summary[:-1] + '...'
                            
                            urgency = urgency_map.get(ticket_key, 'Unknown')
                            cid = extract_cid(summary)
                            issue_category = categorize_issue(summary)
                            
                            # Estimate if ticket has description (based on summary quality)
                            has_description = len(summary) > 50 or 'detailed' in summary.lower()
                            
                            triq_score = calculate_triq_score(summary, has_description, status, assignee)
                            quality_issues = assess_quality_issues(summary, has_description, status, assignee, urgency)
                            action_required = determine_action_required(triq_score, status, assignee, urgency, quality_issues)
                            
                            writer.writerow({
                                'Ticket_Key': ticket_key,
                                'Summary': summary,
                                'Status': status,
                                'Assignee': assignee if assignee != 'UNASSIGNED' else '',
                                'Urgency': urgency,
                                'Priority': 'Normal',  # All tickets show Normal priority
                                'JIRA_URL': f'https://jiramb.atlassian.net/browse/{ticket_key}',
                                'TriQ_Score': triq_score,
                                'Quality_Issues': quality_issues,
                                'Client_CID': cid,
                                'Issue_Category': issue_category,
                                'Action_Required': action_required,
                                'Created_Date': '2024-2025'  # Approximate range
                            })
                            
                            processed += 1
                            if processed % 50 == 0:
                                print(f"Processed {processed} tickets...")
                    
                    except Exception as e:
                        print(f"Error processing line: {line[:50]}... Error: {e}")
                        continue
            
            print(f"Successfully exported {processed} tickets to CSV")
    
    except Exception as e:
        print(f"Error generating CSV: {e}")

if __name__ == "__main__":
    generate_csv()