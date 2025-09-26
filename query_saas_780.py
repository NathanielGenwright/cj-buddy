#!/usr/bin/env python3
import os
import requests
from requests.auth import HTTPBasicAuth
import json

# Get environment variables
JIRA_URL = os.getenv('JIRA_BASE_URL', 'https://jiramb.atlassian.net')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN') or os.getenv('JIRA_TOKEN')

def get_issues_for_version(project, version):
    """Fetch all issues for a specific project and fix version"""
    
    jql = f'project = {project} AND fixVersion = "{version}"'
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Use GET request with JQL in params
    params = {
        'jql': jql,
        'maxResults': 100,
        'fields': 'key,summary,status,issuetype,priority,assignee'
    }
    
    # Using POST request as GET is deprecated
    response = requests.post(
        f"{JIRA_URL}/rest/api/2/search",
        headers=headers,
        json={
            'jql': jql,
            'maxResults': 100,
            'fields': ['key', 'summary', 'status', 'issuetype', 'priority', 'assignee']
        },
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def display_issues(data):
    """Display issues in a formatted way"""
    
    if not data or 'issues' not in data:
        print("No issues found for SAAS version 7.8.0")
        return
    
    issues = data['issues']
    total = data['total']
    
    print(f"\n📋 SAAS PROJECT - VERSION 7.8.0")
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
            assignee = issue['fields'].get('assignee', {}).get('displayName', 'Unassigned') if issue['fields'].get('assignee') else 'Unassigned'
            
            print(f"• [{key}] {summary}")
            print(f"  Type: {issue_type} | Assignee: {assignee}")
    
    # Summary statistics
    print(f"\n📊 SUMMARY BY STATUS")
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
    print("🔍 Fetching SAAS project issues for version 7.8.0...")
    data = get_issues_for_version("SAAS", "7.8.0")
    display_issues(data)