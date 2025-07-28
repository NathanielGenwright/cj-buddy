#!/usr/bin/env python3
import json
from jira_helper import get_issue

ticket_id = "saas-658"
issue = get_issue(ticket_id)

print(f"Issue Key: {issue.get('key', 'Unknown')}")
print(f"Summary: {issue['fields'].get('summary', 'No summary')}")
print("\nDescription structure:")

desc = issue['fields'].get('description')
if desc is None:
    print("Description is None/empty")
else:
    print(f"Description type: {type(desc)}")
    if isinstance(desc, dict):
        print(f"Description keys: {desc.keys()}")
        print("\nFull description object:")
        print(json.dumps(desc, indent=2))