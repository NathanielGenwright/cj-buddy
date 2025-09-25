#!/usr/bin/env python3
"""
List SAAS project issues with fix version 7.8.0 using existing jira_helper
"""

import os
import sys
from jira_helper import search_issues
from datetime import datetime

def list_issues():
    """List all SAAS issues for version 7.8.0"""
    
    # JQL for SAAS project with fix version 7.8.0
    jql = 'project = SAAS AND fixVersion = "7.8.0" ORDER BY priority DESC, created DESC'
    
    print("🔍 Querying SAAS Project Issues with Fix Version 7.8.0")
    print("=" * 70)
    print(f"🔎 JQL: {jql}")
    print("-" * 70)
    
    try:
        # Use the search_issues function from jira_helper
        result = search_issues(jql, max_results=200)
        issues = result.get('issues', [])
        
        if not issues:
            print("ℹ️ No issues found for SAAS version 7.8.0")
            return
        
        print(f"\n📊 Found {len(issues)} issue(s)")
        print("\n📋 Issues List:")
        print("-" * 70)
        
        # Group by status
        status_groups = {}
        for issue in issues:
            status = str(issue.fields.status)
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(issue)
        
        # Display by status
        status_order = ['To Do', 'In Progress', 'Code Review', 'Testing', 'Done', 'Closed']
        
        for status in status_order:
            if status in status_groups:
                print(f"\n🏷️  {status} ({len(status_groups[status])} issues)")
                print("  " + "-" * 66)
                
                for issue in status_groups[status]:
                    key = issue.key
                    summary = str(issue.fields.summary)
                    if len(summary) > 50:
                        summary = summary[:47] + "..."
                    
                    priority = str(issue.fields.priority) if issue.fields.priority else 'None'
                    issue_type = str(issue.fields.issuetype)
                    assignee = str(issue.fields.assignee) if issue.fields.assignee else 'Unassigned'
                    
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
                    
                    print(f"  {type_emoji} {key:<12} {priority_emoji} {summary}")
                    print(f"     👤 {assignee}")
        
        # Display any issues with other statuses
        for status, issues_list in status_groups.items():
            if status not in status_order:
                print(f"\n🏷️  {status} ({len(issues_list)} issues)")
                print("  " + "-" * 66)
                
                for issue in issues_list:
                    key = issue.key
                    summary = str(issue.fields.summary)
                    if len(summary) > 50:
                        summary = summary[:47] + "..."
                    print(f"  📄 {key:<12} {summary}")
        
        # Summary statistics
        print("\n" + "=" * 70)
        print("📊 Summary Statistics:")
        print("-" * 70)
        
        # Issue type breakdown
        type_counts = {}
        for issue in issues:
            issue_type = str(issue.fields.issuetype)
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
        
        print("\n📈 By Issue Type:")
        for issue_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {issue_type}: {count}")
        
        # Priority breakdown
        priority_counts = {}
        for issue in issues:
            priority = str(issue.fields.priority) if issue.fields.priority else 'None'
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        print("\n🎯 By Priority:")
        for priority in ['Highest', 'High', 'Medium', 'Low', 'Lowest', 'None']:
            if priority in priority_counts:
                print(f"  • {priority}: {priority_counts[priority]}")
        
        # Status breakdown
        print("\n📊 By Status:")
        total_issues = len(issues)
        for status, issues_list in sorted(status_groups.items(), key=lambda x: len(x[1]), reverse=True):
            percentage = (len(issues_list) / total_issues) * 100
            print(f"  • {status}: {len(issues_list)} ({percentage:.1f}%)")
        
        # Show sample issue details
        if issues:
            print(f"\n🔍 Sample Issue Details:")
            print("-" * 70)
            sample = issues[0]
            print(f"Key: {sample.key}")
            print(f"Summary: {sample.fields.summary}")
            print(f"Status: {sample.fields.status}")
            print(f"Type: {sample.fields.issuetype}")
            print(f"Priority: {sample.fields.priority}")
            print(f"Assignee: {sample.fields.assignee or 'Unassigned'}")
            if hasattr(sample.fields, 'fixVersions') and sample.fields.fixVersions:
                versions = [str(v) for v in sample.fields.fixVersions]
                print(f"Fix Versions: {', '.join(versions)}")
        
    except Exception as e:
        print(f"❌ Error querying issues: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_issues()