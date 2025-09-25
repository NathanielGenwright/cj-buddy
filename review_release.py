#!/usr/bin/env python3
import os
import requests
from requests.auth import HTTPBasicAuth
import json

# Get environment variables
JIRA_URL = os.getenv('JIRA_BASE_URL', 'https://jiramb.atlassian.net')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN') or os.getenv('JIRA_TOKEN')

def get_release_issues(fix_version):
    """Fetch all issues for a specific release/fix version"""
    
    jql = f'fixVersion = "{fix_version}"'
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    params = {
        'jql': jql,
        'maxResults': 100,
        'fields': 'key,summary,status,issuetype,priority,assignee,reporter,created,updated,description'
    }
    
    response = requests.get(
        f"{JIRA_URL}/rest/api/3/search",
        headers=headers,
        params={
            'jql': jql,
            'maxResults': 100,
            'fields': 'key,summary,status,issuetype,priority,assignee,reporter,created,updated,description'
        },
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def display_release_review(data):
    """Display release issues in a formatted way"""
    
    if not data or 'issues' not in data:
        print("No issues found for this release")
        return
    
    issues = data['issues']
    total = data['total']
    
    print(f"\n📋 RELEASE 7.8.0 REVIEW")
    print("=" * 60)
    print(f"Total Issues: {total}")
    print("=" * 60)
    
    # Group by status
    status_groups = {}
    for issue in issues:
        status = issue['fields']['status']['name']
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(issue)
    
    # Display by status
    for status, status_issues in status_groups.items():
        print(f"\n📌 {status} ({len(status_issues)} issues)")
        print("-" * 40)
        
        for issue in status_issues:
            key = issue['key']
            summary = issue['fields']['summary']
            issue_type = issue['fields']['issuetype']['name']
            priority = issue['fields'].get('priority', {}).get('name', 'N/A') if issue['fields'].get('priority') else 'N/A'
            assignee = issue['fields'].get('assignee', {}).get('displayName', 'Unassigned') if issue['fields'].get('assignee') else 'Unassigned'
            
            print(f"• [{key}] {summary}")
            print(f"  Type: {issue_type} | Priority: {priority} | Assignee: {assignee}")
    
    # Summary statistics
    print(f"\n📊 SUMMARY")
    print("-" * 40)
    for status, status_issues in status_groups.items():
        print(f"{status}: {len(status_issues)}")
    
    # Issue type breakdown
    type_counts = {}
    for issue in issues:
        issue_type = issue['fields']['issuetype']['name']
        type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
    
    print(f"\n📈 ISSUE TYPES")
    print("-" * 40)
    for issue_type, count in type_counts.items():
        print(f"{issue_type}: {count}")

if __name__ == "__main__":
    print("🔍 Fetching Release 7.8.0 issues from Jira...")
    data = get_release_issues("7.8.0")
    display_release_review(data)