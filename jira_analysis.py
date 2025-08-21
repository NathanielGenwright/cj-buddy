#!/usr/bin/env python3
"""
Jira Issue Analysis Script

This script fetches and analyzes multiple Jira issues using the REST API.
Provides statistics, filtering, and export capabilities.
"""

import requests
import json
import os
import sys
import csv
from getpass import getpass
from datetime import datetime
from dateutil import parser
from collections import Counter, defaultdict
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
JIRA_BASE_URL = os.environ.get("JIRA_BASE_URL", "https://your-domain.atlassian.net")
EMAIL = os.environ.get("JIRA_EMAIL", "your-email@example.com")
API_TOKEN = os.environ.get("JIRA_API_TOKEN")

# If API token isn't set in environment, check for config file or prompt
if not API_TOKEN:
    config_file = os.path.expanduser("~/.jira_config.json")
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            JIRA_BASE_URL = config.get("jira_base_url", JIRA_BASE_URL)
            EMAIL = config.get("email", EMAIL)
            API_TOKEN = config.get("api_token", "")
    
    if not API_TOKEN:
        print("\n" + "="*60)
        print("JIRA API TOKEN REQUIRED")
        print("="*60)
        print("\nOptions to provide API token:")
        print("1. Set environment variable: export JIRA_API_TOKEN='your-token'")
        print("2. Create config file at ~/.jira_config.json with format:")
        print('   {"jira_base_url": "https://your-domain.atlassian.net",')
        print('    "email": "your-email@example.com",')
        print('    "api_token": "your-api-token"}')
        print("3. Update the script directly with your credentials")
        print("\nTo get an API token, visit:")
        print("https://id.atlassian.com/manage-profile/security/api-tokens")
        print("="*60)
        sys.exit(1)

# Authentication and headers
auth = (EMAIL, API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def search_issues(jql_query, max_results=100, fields=None):
    """Search for issues using JQL (Jira Query Language)."""
    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    
    if fields is None:
        fields = ["summary", "status", "assignee", "reporter", "created", "updated", 
                 "priority", "issuetype", "description", "resolution", "resolutiondate",
                 "components", "labels", "fixVersions", "customfield_10016"]  # story points
    
    all_issues = []
    start_at = 0
    
    while True:
        params = {
            "jql": jql_query,
            "startAt": start_at,
            "maxResults": min(max_results - len(all_issues), 50),
            "fields": fields
        }
        
        response = requests.get(
            url,
            params=params,
            headers=headers,
            auth=auth
        )
        
        if response.status_code == 200:
            data = response.json()
            issues = data.get("issues", [])
            all_issues.extend(issues)
            
            total = data.get("total", 0)
            print(f"Fetched {len(all_issues)} of {total} issues...")
            
            if len(all_issues) >= total or len(all_issues) >= max_results or not issues:
                break
            
            start_at = len(all_issues)
        else:
            print(f"Failed to search issues: {response.status_code}")
            print(response.text)
            break
    
    return all_issues

def get_issues_by_keys(issue_keys):
    """Fetch multiple issues by their keys."""
    issues = []
    for key in issue_keys:
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{key}"
        
        response = requests.get(
            url,
            headers=headers,
            auth=auth
        )
        
        if response.status_code == 200:
            issues.append(response.json())
            print(f"Fetched issue: {key}")
        else:
            print(f"Failed to get issue {key}: {response.status_code}")
    
    return issues

def analyze_issues(issues):
    """Analyze a list of Jira issues and generate statistics."""
    if not issues:
        print("No issues to analyze.")
        return None
    
    analysis = {
        "total_issues": len(issues),
        "status_distribution": Counter(),
        "type_distribution": Counter(),
        "priority_distribution": Counter(),
        "assignee_distribution": Counter(),
        "reporter_distribution": Counter(),
        "resolution_distribution": Counter(),
        "labels": Counter(),
        "components": Counter(),
        "created_by_month": defaultdict(int),
        "resolved_by_month": defaultdict(int),
        "avg_resolution_time": [],
        "unassigned_count": 0,
        "story_points_total": 0,
        "story_points_by_status": defaultdict(float)
    }
    
    for issue in issues:
        fields = issue.get("fields", {})
        
        # Status
        status = fields.get("status", {}).get("name", "Unknown")
        analysis["status_distribution"][status] += 1
        
        # Issue Type
        issue_type = fields.get("issuetype", {}).get("name", "Unknown")
        analysis["type_distribution"][issue_type] += 1
        
        # Priority
        priority = fields.get("priority", {})
        if priority:
            analysis["priority_distribution"][priority.get("name", "Unknown")] += 1
        
        # Assignee
        assignee = fields.get("assignee")
        if assignee:
            analysis["assignee_distribution"][assignee.get("displayName", "Unknown")] += 1
        else:
            analysis["unassigned_count"] += 1
        
        # Reporter
        reporter = fields.get("reporter", {})
        if reporter:
            analysis["reporter_distribution"][reporter.get("displayName", "Unknown")] += 1
        
        # Resolution
        resolution = fields.get("resolution")
        if resolution:
            analysis["resolution_distribution"][resolution.get("name", "Unresolved")] += 1
        else:
            analysis["resolution_distribution"]["Unresolved"] += 1
        
        # Labels
        labels = fields.get("labels", [])
        for label in labels:
            analysis["labels"][label] += 1
        
        # Components
        components = fields.get("components", [])
        for component in components:
            analysis["components"][component.get("name", "Unknown")] += 1
        
        # Created date
        created = fields.get("created")
        if created:
            created_date = parser.parse(created)
            month_key = created_date.strftime("%Y-%m")
            analysis["created_by_month"][month_key] += 1
        
        # Resolution date and time
        resolution_date = fields.get("resolutiondate")
        if resolution_date and created:
            resolved_date = parser.parse(resolution_date)
            created_date = parser.parse(created)
            resolution_time = (resolved_date - created_date).days
            analysis["avg_resolution_time"].append(resolution_time)
            
            month_key = resolved_date.strftime("%Y-%m")
            analysis["resolved_by_month"][month_key] += 1
        
        # Story points (custom field - adjust field name as needed)
        story_points = fields.get("customfield_10016")
        if story_points:
            analysis["story_points_total"] += story_points
            analysis["story_points_by_status"][status] += story_points
    
    # Calculate average resolution time
    if analysis["avg_resolution_time"]:
        analysis["avg_resolution_time_days"] = sum(analysis["avg_resolution_time"]) / len(analysis["avg_resolution_time"])
    else:
        analysis["avg_resolution_time_days"] = None
    
    return analysis

def print_analysis(analysis):
    """Print analysis results in a formatted way."""
    if not analysis:
        return
    
    print("\n" + "="*60)
    print("JIRA ISSUE ANALYSIS REPORT")
    print("="*60)
    
    print(f"\nTotal Issues: {analysis['total_issues']}")
    print(f"Unassigned Issues: {analysis['unassigned_count']}")
    
    if analysis["story_points_total"]:
        print(f"Total Story Points: {analysis['story_points_total']}")
    
    if analysis["avg_resolution_time_days"]:
        print(f"Average Resolution Time: {analysis['avg_resolution_time_days']:.1f} days")
    
    print("\n--- Status Distribution ---")
    for status, count in analysis["status_distribution"].most_common():
        percentage = (count / analysis["total_issues"]) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    print("\n--- Issue Type Distribution ---")
    for issue_type, count in analysis["type_distribution"].most_common():
        percentage = (count / analysis["total_issues"]) * 100
        print(f"  {issue_type}: {count} ({percentage:.1f}%)")
    
    print("\n--- Priority Distribution ---")
    for priority, count in analysis["priority_distribution"].most_common():
        percentage = (count / analysis["total_issues"]) * 100
        print(f"  {priority}: {count} ({percentage:.1f}%)")
    
    print("\n--- Top 5 Assignees ---")
    for assignee, count in analysis["assignee_distribution"].most_common(5):
        percentage = (count / analysis["total_issues"]) * 100
        print(f"  {assignee}: {count} ({percentage:.1f}%)")
    
    if analysis["labels"]:
        print("\n--- Top 10 Labels ---")
        for label, count in analysis["labels"].most_common(10):
            print(f"  {label}: {count}")
    
    if analysis["components"]:
        print("\n--- Components ---")
        for component, count in analysis["components"].most_common():
            print(f"  {component}: {count}")
    
    if analysis["story_points_by_status"]:
        print("\n--- Story Points by Status ---")
        for status, points in sorted(analysis["story_points_by_status"].items()):
            print(f"  {status}: {points}")

def export_to_csv(issues, filename="jira_issues_export.csv"):
    """Export issues to CSV file."""
    if not issues:
        print("No issues to export.")
        return
    
    # Flatten the issue data for CSV export
    flattened_data = []
    for issue in issues:
        fields = issue.get("fields", {})
        row = {
            "Key": issue.get("key"),
            "Summary": fields.get("summary"),
            "Status": fields.get("status", {}).get("name"),
            "Type": fields.get("issuetype", {}).get("name"),
            "Priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
            "Assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else "Unassigned",
            "Reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
            "Created": fields.get("created"),
            "Updated": fields.get("updated"),
            "Resolution": fields.get("resolution", {}).get("name") if fields.get("resolution") else "Unresolved",
            "Resolution Date": fields.get("resolutiondate"),
            "Labels": ", ".join(fields.get("labels", [])),
            "Components": ", ".join([c.get("name", "") for c in fields.get("components", [])]),
            "Story Points": fields.get("customfield_10016"),
            "Description": fields.get("description", {}).get("content", [{}])[0].get("content", [{}])[0].get("text", "") if isinstance(fields.get("description"), dict) else fields.get("description")
        }
        flattened_data.append(row)
    
    # Write to CSV
    df = pd.DataFrame(flattened_data)
    df.to_csv(filename, index=False)
    print(f"\nExported {len(issues)} issues to {filename}")

def export_to_json(issues, filename="jira_issues_export.json"):
    """Export issues to JSON file."""
    if not issues:
        print("No issues to export.")
        return
    
    with open(filename, 'w') as f:
        json.dump(issues, f, indent=2, default=str)
    print(f"\nExported {len(issues)} issues to {filename}")

def export_analysis_to_json(analysis, filename="jira_analysis_report.json"):
    """Export analysis results to JSON file."""
    if not analysis:
        print("No analysis to export.")
        return
    
    # Convert Counter objects to dictionaries for JSON serialization
    export_data = {
        "total_issues": analysis["total_issues"],
        "unassigned_count": analysis["unassigned_count"],
        "story_points_total": analysis["story_points_total"],
        "avg_resolution_time_days": analysis["avg_resolution_time_days"],
        "status_distribution": dict(analysis["status_distribution"]),
        "type_distribution": dict(analysis["type_distribution"]),
        "priority_distribution": dict(analysis["priority_distribution"]),
        "assignee_distribution": dict(analysis["assignee_distribution"]),
        "reporter_distribution": dict(analysis["reporter_distribution"]),
        "resolution_distribution": dict(analysis["resolution_distribution"]),
        "labels": dict(analysis["labels"]),
        "components": dict(analysis["components"]),
        "created_by_month": dict(analysis["created_by_month"]),
        "resolved_by_month": dict(analysis["resolved_by_month"]),
        "story_points_by_status": dict(analysis["story_points_by_status"])
    }
    
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    print(f"\nExported analysis report to {filename}")

def main():
    """Main function with menu for different operations."""
    print("\n" + "="*60)
    print("JIRA ISSUE ANALYSIS TOOL")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Search issues using JQL query")
        print("2. Analyze specific issue keys")
        print("3. Analyze issues from a project")
        print("4. Analyze issues assigned to a user")
        print("5. Analyze issues created in date range")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ")
        
        if choice == "1":
            jql = input("Enter JQL query: ")
            max_results = int(input("Maximum results to fetch (default 100): ") or "100")
            issues = search_issues(jql, max_results)
            
        elif choice == "2":
            keys_input = input("Enter issue keys (comma-separated, e.g., PROJ-1,PROJ-2): ")
            issue_keys = [key.strip() for key in keys_input.split(",")]
            issues = get_issues_by_keys(issue_keys)
            
        elif choice == "3":
            project = input("Enter project key: ")
            jql = f"project = {project}"
            max_results = int(input("Maximum results to fetch (default 100): ") or "100")
            issues = search_issues(jql, max_results)
            
        elif choice == "4":
            assignee = input("Enter assignee email or username: ")
            jql = f"assignee = '{assignee}'"
            max_results = int(input("Maximum results to fetch (default 100): ") or "100")
            issues = search_issues(jql, max_results)
            
        elif choice == "5":
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            project = input("Enter project key (optional, press Enter to skip): ")
            
            jql = f"created >= '{start_date}' AND created <= '{end_date}'"
            if project:
                jql += f" AND project = {project}"
            
            max_results = int(input("Maximum results to fetch (default 100): ") or "100")
            issues = search_issues(jql, max_results)
            
        elif choice == "6":
            print("Exiting...")
            break
            
        else:
            print("Invalid option. Please try again.")
            continue
        
        if issues:
            # Analyze the issues
            analysis = analyze_issues(issues)
            print_analysis(analysis)
            
            # Export options
            print("\nExport Options:")
            print("1. Export issues to CSV")
            print("2. Export issues to JSON")
            print("3. Export analysis report to JSON")
            print("4. All exports")
            print("5. Skip export")
            
            export_choice = input("\nSelect export option (1-5): ")
            
            if export_choice == "1":
                filename = input("Enter CSV filename (default: jira_issues_export.csv): ") or "jira_issues_export.csv"
                export_to_csv(issues, filename)
            elif export_choice == "2":
                filename = input("Enter JSON filename (default: jira_issues_export.json): ") or "jira_issues_export.json"
                export_to_json(issues, filename)
            elif export_choice == "3":
                filename = input("Enter JSON filename (default: jira_analysis_report.json): ") or "jira_analysis_report.json"
                export_analysis_to_json(analysis, filename)
            elif export_choice == "4":
                csv_file = input("Enter CSV filename (default: jira_issues_export.csv): ") or "jira_issues_export.csv"
                json_file = input("Enter JSON filename (default: jira_issues_export.json): ") or "jira_issues_export.json"
                report_file = input("Enter analysis report filename (default: jira_analysis_report.json): ") or "jira_analysis_report.json"
                export_to_csv(issues, csv_file)
                export_to_json(issues, json_file)
                export_analysis_to_json(analysis, report_file)

if __name__ == "__main__":
    main()