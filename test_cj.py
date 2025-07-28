#!/usr/bin/env python3
import os
from dotenv import load_dotenv
load_dotenv()

# Test environment variables
print("Environment check:")
print(f"JIRA_BASE_URL: {os.getenv('JIRA_BASE_URL')}")
print(f"JIRA_EMAIL: {os.getenv('JIRA_EMAIL')}")
print(f"JIRA_TOKEN: {os.getenv('JIRA_TOKEN')[:10]}..." if os.getenv('JIRA_TOKEN') else "JIRA_TOKEN: None")
print(f"CLAUDE_API_KEY: {os.getenv('CLAUDE_API_KEY')[:10]}..." if os.getenv('CLAUDE_API_KEY') else "CLAUDE_API_KEY: None")

# Test Jira connection
from jira_helper import get_issue
print("\nTesting Jira connection...")
try:
    issue = get_issue("SAAS-1739")
    print(f"Success! Found issue: {issue.get('key', 'Unknown')}")
    if 'fields' in issue:
        print(f"Summary: {issue['fields'].get('summary', 'No summary')}")
except Exception as e:
    print(f"Jira error: {e}")

# Test Claude connection
print("\nTesting Claude connection...")
from claude_helper import get_claude_response
try:
    response = get_claude_response("Say 'Hello, CJ-Buddy is working!' in 5 words or less.")
    print(f"Claude response: {response}")
except Exception as e:
    print(f"Claude error: {e}")