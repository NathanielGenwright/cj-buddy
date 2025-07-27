
import os
import requests
from dotenv import load_dotenv
load_dotenv()

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")

def get_issue(ticket_id):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
    response = requests.get(url, auth=(JIRA_EMAIL, JIRA_TOKEN), headers={"Accept": "application/json"})
    return response.json()

def post_comment(ticket_id, body):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"
    payload = {"body": body}
    requests.post(url, auth=(JIRA_EMAIL, JIRA_TOKEN), json=payload)

def add_label(ticket_id, label):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
    payload = {
        "update": {
            "labels": [{"add": label}]
        }
    }
    headers = {"Content-Type": "application/json"}
    requests.put(url, auth=(JIRA_EMAIL, JIRA_TOKEN), json=payload, headers=headers)
