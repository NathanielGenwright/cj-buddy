#!/usr/bin/env python3
"""
Jira Automation Script

This script demonstrates how to create and comment on Jira issues using the REST API.
"""

import requests
import json
import os
from getpass import getpass

# Configuration
JIRA_BASE_URL = "https://your-domain.atlassian.net"  # Replace with your Jira URL
EMAIL = "your-email@example.com"  # Replace with your Atlassian email
API_TOKEN = os.environ.get("JIRA_API_TOKEN")  # Set this as an environment variable for security

# If API token isn't set in environment, prompt for it
if not API_TOKEN:
    API_TOKEN = getpass("Enter your Atlassian API token: ")

# Authentication and headers
auth = (EMAIL, API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def create_issue(project_key, summary, description, issue_type="Task"):
    """Create a new Jira issue."""
    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": issue_type
            }
        }
    }
    
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 201:
        issue_data = response.json()
        print(f"Issue created successfully: {issue_data['key']}")
        return issue_data['key']
    else:
        print(f"Failed to create issue: {response.status_code}")
        print(response.text)
        return None

def add_comment(issue_key, comment_text):
    """Add a comment to an existing Jira issue."""
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment"
    
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": comment_text
                        }
                    ]
                }
            ]
        }
    }
    
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 201:
        comment_data = response.json()
        print(f"Comment added successfully: {comment_data['id']}")
        return True
    else:
        print(f"Failed to add comment: {response.status_code}")
        print(response.text)
        return False

def get_issue(issue_key):
    """Get details of a Jira issue."""
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
    
    response = requests.get(
        url,
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 200:
        issue_data = response.json()
        print(f"Issue found: {issue_data['fields']['summary']}")
        return issue_data
    else:
        print(f"Failed to get issue: {response.status_code}")
        print(response.text)
        return None

def main():
    # Example usage
    project_key = input("Enter project key (e.g., 'PROJ'): ")
    
    # Create a new issue
    summary = "Automated Issue Creation"
    description = "This issue was created using a Python script and the Jira REST API."
    issue_key = create_issue(project_key, summary, description)
    
    if issue_key:
        # Add a comment to the created issue
        comment_text = "This is an automated comment added via the API."
        add_comment(issue_key, comment_text)
        
        # Get issue details
        get_issue(issue_key)

if __name__ == "__main__":
    main()
