#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

JIRA_URL = os.getenv('JIRA_BASE_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_TOKEN = os.getenv('JIRA_API_TOKEN')

# Search for 7.8.0 issues
url = f"{JIRA_URL}/rest/api/3/search"
params = {
    'jql': 'fixVersion = "7.8.0"',
    'maxResults': 100,
    'fields': 'key,summary,status,issuetype,priority,assignee'
}

response = requests.get(url, params=params, auth=(JIRA_EMAIL, JIRA_TOKEN))

if response.status_code == 200:
    data = response.json()
    total = data.get('total', len(data.get('issues', [])))
    print(f"\n📋 RELEASE 7.8.0 ISSUES")
    print("=" * 60)
    print(f"Total Issues: {total}")
    print("=" * 60)
    
    for issue in data.get('issues', []):
        key = issue.get('key', 'N/A')
        fields = issue.get('fields', {})
        summary = fields.get('summary', 'No summary')
        status = fields.get('status', {}).get('name', 'Unknown')
        issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
        priority = fields.get('priority', {}).get('name', 'N/A') if fields.get('priority') else 'N/A'
        assignee = fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned'
        
        print(f"\n• [{key}] {summary}")
        print(f"  Status: {status} | Type: {issue_type} | Priority: {priority}")
        print(f"  Assignee: {assignee}")
else:
    print(f"Error: {response.text}")