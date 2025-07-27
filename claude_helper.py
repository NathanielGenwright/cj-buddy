
import os
import requests
from dotenv import load_dotenv
load_dotenv()

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

def get_claude_response(prompt):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    data = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 400,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['content'][0]['text']
