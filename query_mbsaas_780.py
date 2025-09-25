#!/usr/bin/env python3
"""
Query Jira for MBSAAS project issues with fix version 7.8.0
"""

import os
import requests
import json
from dotenv import load_dotenv
from base64 import b64encode
from datetime import datetime

# Load environment variables
load_dotenv()

def create_auth_header():
    """Create authentication header"""
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN') or os.getenv('JIRA_TOKEN')
    
    if not email or not api_token:
        print("❌ Missing credentials")
        return None
    
    auth_string = f"{email}:{api_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = b64encode(auth_bytes).decode('ascii')
    
    return f'Basic {auth_b64}'

def query_issues():
    """Query issues for MBSAAS project with fix version 7.8.0"""
    
    jira_base_url = os.getenv('JIRA_BASE_URL', 'https://jiramb.atlassian.net')
    auth_header = create_auth_header()
    
    if not auth_header:
        return
    
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # JQL query for SAAS project (trying different project key formats)
    # MBSAAS might be SAAS or another format
    jql = 'project = SAAS AND fixVersion = "7.8.0" ORDER BY priority DESC, created DESC'
    
    # Fields to retrieve
    fields = [
        'summary',
        'status',
        'priority',
        'assignee',
        'reporter',
        'created',
        'updated',
        'fixVersions',
        'issuetype',
        'description',
        'customfield_10029',  # Story Points
        'components'
    ]
    
    # API endpoint for search - using latest endpoint
    search_url = f"{jira_base_url}/rest/api/latest/search"
    
    # Parameters for the search
    params = {
        'jql': jql,
        'fields': ','.join(fields),
        'maxResults': 100,
        'startAt': 0
    }
    
    print("🔍 Querying MBSAAS Project Issues with Fix Version 7.8.0")
    print("=" * 70)
    print(f"📍 Jira URL: {jira_base_url}")
    print(f"🔎 JQL: {jql}")
    print("-" * 70)
    
    all_issues = []
    total_issues = 0
    
    try:
        while True:
            # Use POST method for search as per new API requirements
            payload = {
                'jql': jql,
                'fields': fields,
                'maxResults': params['maxResults'],
                'startAt': params['startAt']
            }
            response = requests.post(search_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get('issues', [])
                total = data.get('total', 0)
                
                if params['startAt'] == 0:
                    total_issues = total
                    print(f"\n📊 Found {total} issue(s) in total\n")
                
                all_issues.extend(issues)
                
                # Check if we need to fetch more
                if params['startAt'] + len(issues) < total:
                    params['startAt'] += len(issues)
                else:
                    break
            else:
                print(f"❌ Error: Status code {response.status_code}")
                print(f"Response: {response.text}")
                return
                
        # Process and display the issues
        if all_issues:
            print("📋 Issues List:")
            print("-" * 70)
            
            # Group by status
            status_groups = {}
            for issue in all_issues:
                status = issue['fields']['status']['name']
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(issue)
            
            # Display by status
            status_order = ['To Do', 'In Progress', 'In Review', 'Testing', 'Done', 'Closed']
            
            for status in status_order:
                if status in status_groups:
                    print(f"\n🏷️  {status} ({len(status_groups[status])} issues)")
                    print("  " + "-" * 66)
                    
                    for issue in status_groups[status]:
                        key = issue['key']
                        summary = issue['fields']['summary'][:50] + "..." if len(issue['fields']['summary']) > 50 else issue['fields']['summary']
                        priority = issue['fields']['priority']['name'] if issue['fields']['priority'] else 'None'
                        issue_type = issue['fields']['issuetype']['name']
                        assignee = issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned'
                        
                        # Get priority emoji
                        priority_emoji = {
                            'Highest': '🔴',
                            'High': '🟠',
                            'Medium': '🟡',
                            'Low': '🟢',
                            'Lowest': '⚪'
                        }.get(priority, '⚫')
                        
                        # Get issue type emoji
                        type_emoji = {
                            'Bug': '🐛',
                            'Story': '📖',
                            'Task': '📋',
                            'Epic': '🎯',
                            'Sub-task': '📎',
                            'Improvement': '⚡',
                            'New Feature': '✨'
                        }.get(issue_type, '📄')
                        
                        print(f"  {type_emoji} {key:<12} {priority_emoji} {summary:<45}")
                        print(f"     👤 {assignee}")
            
            # Display any issues with other statuses
            for status, issues in status_groups.items():
                if status not in status_order:
                    print(f"\n🏷️  {status} ({len(issues)} issues)")
                    print("  " + "-" * 66)
                    
                    for issue in issues:
                        key = issue['key']
                        summary = issue['fields']['summary'][:50] + "..." if len(issue['fields']['summary']) > 50 else issue['fields']['summary']
                        print(f"  📄 {key:<12} {summary}")
            
            # Summary statistics
            print("\n" + "=" * 70)
            print("📊 Summary Statistics:")
            print("-" * 70)
            
            # Issue type breakdown
            type_counts = {}
            for issue in all_issues:
                issue_type = issue['fields']['issuetype']['name']
                type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
            
            print("\n📈 By Issue Type:")
            for issue_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {issue_type}: {count}")
            
            # Priority breakdown
            priority_counts = {}
            for issue in all_issues:
                priority = issue['fields']['priority']['name'] if issue['fields']['priority'] else 'None'
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            print("\n🎯 By Priority:")
            for priority in ['Highest', 'High', 'Medium', 'Low', 'Lowest', 'None']:
                if priority in priority_counts:
                    print(f"  • {priority}: {priority_counts[priority]}")
            
            # Status breakdown
            print("\n📊 By Status:")
            for status, issues in sorted(status_groups.items(), key=lambda x: len(x[1]), reverse=True):
                percentage = (len(issues) / total_issues) * 100
                print(f"  • {status}: {len(issues)} ({percentage:.1f}%)")
            
            # Save to file
            output_file = f"mbsaas_780_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(all_issues, f, indent=2)
            print(f"\n💾 Full issue data saved to: {output_file}")
            
        else:
            print("ℹ️ No issues found matching the criteria")
            
    except Exception as e:
        print(f"❌ Error querying issues: {e}")

if __name__ == "__main__":
    query_issues()