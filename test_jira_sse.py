#!/usr/bin/env python3
"""
Test script to find and connect to SSE endpoints on your Jira instance
"""

import os
import requests
import json
from dotenv import load_dotenv
from base64 import b64encode

# Load environment variables
load_dotenv()

def create_auth_header():
    """Create authentication header"""
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN') or os.getenv('JIRA_TOKEN')
    
    if not email or not api_token:
        return None
    
    auth_string = f"{email}:{api_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = b64encode(auth_bytes).decode('ascii')
    
    return f'Basic {auth_b64}'

def test_endpoints():
    """Test various potential SSE endpoints"""
    
    jira_base_url = os.getenv('JIRA_BASE_URL', 'https://jiramb.atlassian.net')
    auth_header = create_auth_header()
    
    if not auth_header:
        print("❌ Missing credentials")
        return
    
    # List of potential SSE endpoints to test
    endpoints = [
        f"{jira_base_url}/rest/api/3/events",
        f"{jira_base_url}/rest/api/3/sse",
        f"{jira_base_url}/rest/api/2/events",
        f"{jira_base_url}/rest/webhooks/1.0/webhook",
        f"{jira_base_url}/rest/api/3/webhook",
        f"{jira_base_url}/v1/sse",
        "https://mcp.atlassian.com/v1/sse",
        "https://api.atlassian.com/ex/jira/{cloud-id}/rest/api/3/events"
    ]
    
    print("🔍 Searching for SSE/Event endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints:
        print(f"\n📡 Testing: {endpoint}")
        
        try:
            # Try with different accept headers
            for accept_header in ['text/event-stream', 'application/json']:
                headers = {
                    'Authorization': auth_header,
                    'Accept': accept_header
                }
                
                response = requests.get(
                    endpoint,
                    headers=headers,
                    timeout=5,
                    stream=True if accept_header == 'text/event-stream' else False
                )
                
                if response.status_code == 200:
                    print(f"  ✅ Success with Accept: {accept_header}")
                    if accept_header == 'application/json':
                        try:
                            data = response.json()
                            print(f"  📄 Response: {json.dumps(data, indent=2)[:200]}...")
                        except:
                            print(f"  📄 Response: {response.text[:200]}...")
                    break
                elif response.status_code == 404:
                    continue
                else:
                    print(f"  ⚠️ Status {response.status_code} with Accept: {accept_header}")
                    
        except requests.exceptions.Timeout:
            print(f"  ⏱️ Timeout")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection error")
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}")

def check_webhook_support():
    """Check if webhooks are available (alternative to SSE)"""
    
    jira_base_url = os.getenv('JIRA_BASE_URL', 'https://jiramb.atlassian.net')
    auth_header = create_auth_header()
    
    if not auth_header:
        return
    
    print("\n\n🔍 Checking Webhook Support...")
    print("=" * 50)
    
    webhook_url = f"{jira_base_url}/rest/webhooks/1.0/webhook"
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(webhook_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Webhooks are supported!")
            webhooks = response.json()
            if webhooks:
                print(f"📋 Found {len(webhooks)} webhook(s)")
                for webhook in webhooks[:3]:  # Show first 3
                    print(f"  - {webhook.get('name', 'Unnamed')}: {webhook.get('url', 'No URL')}")
            else:
                print("📋 No webhooks configured")
        elif response.status_code == 403:
            print("⚠️ Webhooks require admin permissions")
        else:
            print(f"❌ Webhook endpoint returned: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking webhooks: {e}")

def check_cloud_id():
    """Get the cloud ID for your Atlassian instance"""
    
    jira_base_url = os.getenv('JIRA_BASE_URL', 'https://jiramb.atlassian.net')
    auth_header = create_auth_header()
    
    if not auth_header:
        return None
    
    print("\n\n🔍 Getting Cloud Instance Information...")
    print("=" * 50)
    
    # Try to get cloud ID from accessible resources
    accessible_resources_url = "https://api.atlassian.com/oauth/token/accessible-resources"
    
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json'
    }
    
    try:
        # First, try to get serverInfo
        server_info_url = f"{jira_base_url}/rest/api/3/serverInfo"
        response = requests.get(server_info_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Server Info Retrieved")
            print(f"  📍 Base URL: {info.get('baseUrl', 'Unknown')}")
            print(f"  📅 Version: {info.get('version', 'Unknown')}")
            print(f"  🏢 Deployment: {info.get('deploymentType', 'Unknown')}")
            
            # For cloud instances, we might be able to extract cloud ID
            if 'deploymentType' in info and info['deploymentType'] == 'Cloud':
                print(f"  ☁️ This is a Cloud instance")
        else:
            print(f"⚠️ Could not retrieve server info: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting instance info: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 Jira SSE/Event Endpoint Discovery")
    print("=" * 50)
    
    # Test various endpoints
    test_endpoints()
    
    # Check webhook support as alternative
    check_webhook_support()
    
    # Get cloud instance info
    check_cloud_id()
    
    print("\n\n📊 Summary")
    print("=" * 50)
    print("If no SSE endpoints were found, you can use:")
    print("  1. Webhooks (if you have admin access)")
    print("  2. Polling the REST API periodically")
    print("  3. Jira's built-in automation rules")
    print("\nNote: SSE support varies by Atlassian product and deployment type.")