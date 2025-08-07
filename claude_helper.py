import os
import requests
from dotenv import load_dotenv
load_dotenv()

CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def get_claude_response(prompt):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 2000,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if 'error' in result:
        return f"Error: {result['error'].get('message', 'Unknown error')}"
    
    if 'content' in result and len(result['content']) > 0:
        return result['content'][0]['text']
    else:
        return "Error: Unexpected response format"