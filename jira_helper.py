import os
import requests
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")

def get_issue(ticket_id):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
    response = requests.get(url, auth=(JIRA_EMAIL, JIRA_TOKEN), headers={"Accept": "application/json"})
    return response.json()

def post_comment(ticket_id, body):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"
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
                            "text": body
                        }
                    ]
                }
            ]
        }
    }
    response = requests.post(url, auth=(JIRA_EMAIL, JIRA_TOKEN), json=payload)
    if response.status_code != 201:
        raise Exception(f"HTTP {response.status_code}: {response.text}")
    return response

def add_label(ticket_id, label):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
    payload = {
        "update": {
            "labels": [{"add": label}]
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, auth=(JIRA_EMAIL, JIRA_TOKEN), json=payload, headers=headers)
    if response.status_code != 204:
        raise Exception(f"HTTP {response.status_code}: {response.text}")
    return response

def search_issues(jql, max_results=100):
    """Search for issues using JQL"""
    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    
    payload = {
        "jql": jql,
        "maxResults": max_results,
        "fields": [
            "key",
            "summary", 
            "status",
            "priority",
            "issuetype",
            "assignee",
            "reporter",
            "created",
            "updated",
            "fixVersions",
            "components"
        ]
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, auth=(JIRA_EMAIL, JIRA_TOKEN), json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

def update_field(ticket_id, field_id, value):
    """Update a custom field in a Jira issue"""
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
    payload = {
        "fields": {
            field_id: value
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, auth=(JIRA_EMAIL, JIRA_TOKEN), json=payload, headers=headers)
    if response.status_code != 204:
        raise Exception(f"HTTP {response.status_code}: {response.text}")
    return response