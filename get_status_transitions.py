#!/usr/bin/env python3
import subprocess
import json
import sys
from datetime import datetime

def parse_jira_date(date_str):
    if not date_str:
        return None
    # Parse JIRA date format: 2025-05-22T12:03:13.891-0400
    try:
        # Remove timezone info for parsing
        clean_date = date_str.split('T')[0] + 'T' + date_str.split('T')[1].split('-')[0].split('+')[0]
        return datetime.fromisoformat(clean_date.replace('Z', ''))
    except:
        return date_str

def get_ticket_details(ticket_key):
    """Get all available details for a ticket"""
    try:
        cmd = f'acli jira workitem view {ticket_key} --fields "*all" --json'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            fields = data.get("fields", {})
            
            # Extract status information
            status_info = {
                "key": ticket_key,
                "created": fields.get("created"),
                "updated": fields.get("updated"), 
                "current_status": fields.get("status", {}).get("name"),
                "status_category": fields.get("status", {}).get("statusCategory", {}).get("name"),
                "status_category_change_date": fields.get("statuscategorychangedate"),
                "assignee": fields.get("assignee", {}).get("emailAddress") if fields.get("assignee") else None,
                "priority": fields.get("priority", {}).get("name"),
                "issuetype": fields.get("issuetype", {}).get("name"),
                "summary": fields.get("summary"),
                "resolution": fields.get("resolution", {}).get("name") if fields.get("resolution") else None,
                "resolutiondate": fields.get("resolutiondate")
            }
            
            # Look for any workflow transition indicators in custom fields
            for field_name, field_value in fields.items():
                if 'transition' in field_name.lower() or 'workflow' in field_name.lower():
                    status_info[field_name] = field_value
            
            return status_info
        else:
            print(f"Error fetching {ticket_key}: {result.stderr}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Exception for {ticket_key}: {e}", file=sys.stderr)
        return None

def calculate_phase_duration(created_date, status_change_date, current_date=None):
    """Calculate duration between dates"""
    if not created_date or not status_change_date:
        return None
    
    try:
        start = parse_jira_date(created_date)
        end = parse_jira_date(status_change_date)
        if current_date:
            end = parse_jira_date(current_date)
        
        if start and end:
            duration = end - start
            return duration.days
    except:
        pass
    return None

# All tickets from SAAS-1354 analysis
tickets = [
    "SAAS-1354",  # Main ticket
    "TRI-1998", "TRI-1573", "SAAS-2165", "SAAS-2128", "SAAS-1952",
    "SAAS-1951", "SAAS-1858", "SAAS-1820", "SAAS-1784", "SAAS-1779",
    "SAAS-1768", "SAAS-1751", "SAAS-1725", "SAAS-1706", "SAAS-1705", "SAAS-559"
]

print("# Status Transition Analysis for SAAS-1354 and Linked Tickets")
print()

all_results = []

for ticket in tickets:
    print(f"Analyzing {ticket}...", file=sys.stderr)
    details = get_ticket_details(ticket)
    if details:
        all_results.append(details)

# Sort by created date
all_results.sort(key=lambda x: x.get("created", ""))

# Group by status for analysis
status_groups = {
    "To Do": [],
    "In Progress": [], 
    "QA In Progress": [],
    "Ready For QA": [],
    "Ready for Acceptance": [],
    "Done": [],
    "Resolved": [],
    "Canceled": []
}

print("## Current Status Distribution")
print()

for result in all_results:
    status = result.get("current_status", "Unknown")
    if status in status_groups:
        status_groups[status].append(result)
    else:
        print(f"Unknown status: {status} for {result['key']}")

for status, tickets in status_groups.items():
    if tickets:
        print(f"### {status} ({len(tickets)} tickets)")
        for ticket in tickets:
            created = ticket.get("created", "")[:10]  # Just date part
            status_change = ticket.get("status_category_change_date", "")[:10] if ticket.get("status_category_change_date") else "N/A"
            print(f"- **{ticket['key']}**: {ticket.get('summary', '')[:60]}...")
            print(f"  - Created: {created}")
            print(f"  - Status Changed: {status_change}")
            print(f"  - Priority: {ticket.get('priority', 'N/A')}")
            
            # Calculate time in current status
            if ticket.get("status_category_change_date"):
                days_in_status = calculate_phase_duration(
                    ticket.get("status_category_change_date"),
                    datetime.now().isoformat()
                )
                if days_in_status is not None:
                    print(f"  - Days in current status: {days_in_status}")
            print()

print("## Detailed Analysis")
print(json.dumps(all_results, indent=2))