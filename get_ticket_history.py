#!/usr/bin/env python3
import subprocess
import json
import sys
from datetime import datetime

tickets = [
    "SAAS-1354",  # Main ticket
    "TRI-1998", "TRI-1573", "SAAS-2165", "SAAS-2128", "SAAS-1952",
    "SAAS-1951", "SAAS-1858", "SAAS-1820", "SAAS-1784", "SAAS-1779",
    "SAAS-1768", "SAAS-1751", "SAAS-1725", "SAAS-1706", "SAAS-1705", "SAAS-559"
]

results = []

for ticket in tickets:
    print(f"Fetching {ticket}...", file=sys.stderr)
    try:
        cmd = f'acli jira workitem view {ticket} --fields "*all" --json'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            ticket_info = {
                "key": ticket,
                "created": data.get("fields", {}).get("created"),
                "updated": data.get("fields", {}).get("updated"),
                "status": data.get("fields", {}).get("status", {}).get("name"),
                "summary": data.get("fields", {}).get("summary"),
                "priority": data.get("fields", {}).get("priority", {}).get("name"),
                "assignee": data.get("fields", {}).get("assignee", {}).get("emailAddress") if data.get("fields", {}).get("assignee") else None,
                "issuetype": data.get("fields", {}).get("issuetype", {}).get("name"),
                "statuscategorychangedate": data.get("fields", {}).get("statuscategorychangedate")
            }
            results.append(ticket_info)
        else:
            print(f"Error fetching {ticket}: {result.stderr}", file=sys.stderr)
    except Exception as e:
        print(f"Exception for {ticket}: {e}", file=sys.stderr)

# Sort by created date
results.sort(key=lambda x: x.get("created", ""))

print(json.dumps(results, indent=2))