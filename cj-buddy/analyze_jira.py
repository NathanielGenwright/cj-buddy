#!/usr/bin/env python3
"""
Wrapper script to run Jira analysis programmatically
"""

import sys
from jira_analysis import search_issues, analyze_issues, print_analysis, export_to_csv, export_to_json, export_analysis_to_json

def analyze_project(project_key, max_results=100):
    """Analyze all issues in a project."""
    print(f"\nAnalyzing project: {project_key}")
    jql = f"project = {project_key}"
    issues = search_issues(jql, max_results)
    
    if issues:
        analysis = analyze_issues(issues)
        print_analysis(analysis)
        return issues, analysis
    return None, None

def analyze_recent_issues(project_key=None, days=30, max_results=100):
    """Analyze issues created in the last N days."""
    jql = f"created >= '-{days}d'"
    if project_key:
        jql += f" AND project = {project_key}"
    
    print(f"\nAnalyzing issues created in last {days} days")
    issues = search_issues(jql, max_results)
    
    if issues:
        analysis = analyze_issues(issues)
        print_analysis(analysis)
        return issues, analysis
    return None, None

def analyze_user_issues(assignee, max_results=100):
    """Analyze issues assigned to a specific user."""
    print(f"\nAnalyzing issues assigned to: {assignee}")
    jql = f"assignee = '{assignee}'"
    issues = search_issues(jql, max_results)
    
    if issues:
        analysis = analyze_issues(issues)
        print_analysis(analysis)
        return issues, analysis
    return None, None

def analyze_with_jql(jql_query, max_results=100):
    """Analyze issues using custom JQL."""
    print(f"\nAnalyzing with JQL: {jql_query}")
    issues = search_issues(jql_query, max_results)
    
    if issues:
        analysis = analyze_issues(issues)
        print_analysis(analysis)
        return issues, analysis
    return None, None

if __name__ == "__main__":
    # Example usage - analyze SAAS project
    print("="*60)
    print("JIRA ANALYSIS - SAAS PROJECT")
    print("="*60)
    
    # Analyze SAAS project
    issues, analysis = analyze_project("SAAS", max_results=50)
    
    if issues:
        # Export results
        export_to_csv(issues, "saas_issues.csv")
        export_to_json(issues, "saas_issues.json")
        export_analysis_to_json(analysis, "saas_analysis.json")
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        print(f"Total issues analyzed: {len(issues)}")
        print("Exported files:")
        print("  - saas_issues.csv")
        print("  - saas_issues.json")
        print("  - saas_analysis.json")
    
    # You can also analyze recent issues
    print("\n" + "="*60)
    print("RECENT ISSUES (LAST 7 DAYS)")
    print("="*60)
    recent_issues, recent_analysis = analyze_recent_issues("SAAS", days=7, max_results=20)