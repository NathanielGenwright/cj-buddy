#!/usr/bin/env python3
"""
Test script to connect to Atlassian MCP SSE endpoint
"""

import os
import requests
import json
from dotenv import load_dotenv
from base64 import b64encode
import time

# Load environment variables
load_dotenv()

def test_mcp_sse_connection():
    """Test connection to MCP SSE endpoint"""
    
    # Configuration
    mcp_base_url = "https://mcp.atlassian.com"
    sse_endpoint = f"{mcp_base_url}/v1/sse"
    
    # Get credentials from environment
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN') or os.getenv('JIRA_TOKEN')
    
    if not email or not api_token:
        print("❌ Missing credentials. Please set JIRA_EMAIL and JIRA_API_TOKEN in .env file")
        return False
    
    # Create auth header
    auth_string = f"{email}:{api_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }
    
    print(f"🔗 Connecting to MCP SSE endpoint: {sse_endpoint}")
    print(f"📧 Using email: {email}")
    print("-" * 50)
    
    try:
        # First, test basic API access
        test_url = f"{mcp_base_url}/v1/status"
        print(f"📡 Testing basic API access to {test_url}...")
        
        test_response = requests.get(
            test_url,
            headers={'Authorization': f'Basic {auth_b64}'},
            timeout=10
        )
        
        if test_response.status_code == 200:
            print("✅ Basic API access successful")
        else:
            print(f"⚠️ API returned status code: {test_response.status_code}")
            print(f"Response: {test_response.text}")
        
        # Now test SSE connection
        print(f"\n📡 Attempting SSE connection to {sse_endpoint}...")
        
        # Use stream=True for SSE
        response = requests.get(
            sse_endpoint,
            headers=headers,
            stream=True,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Successfully connected to SSE endpoint!")
            print("\n📨 Listening for events (10 seconds)...")
            
            # Read events for 10 seconds
            start_time = time.time()
            event_count = 0
            
            for line in response.iter_lines():
                if time.time() - start_time > 10:
                    break
                    
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        event_count += 1
                        event_data = decoded_line[5:].strip()
                        print(f"  📩 Event {event_count}: {event_data[:100]}...")
                    elif decoded_line.startswith('event:'):
                        print(f"  🏷️ Event type: {decoded_line[6:].strip()}")
            
            if event_count == 0:
                print("  ℹ️ No events received in 10 seconds (this is normal if no events are occurring)")
            else:
                print(f"  📊 Received {event_count} events")
                
            return True
            
        elif response.status_code == 401:
            print("❌ Authentication failed. Please check your credentials.")
            return False
        elif response.status_code == 403:
            print("❌ Access forbidden. You may not have permission to access this endpoint.")
            return False
        elif response.status_code == 404:
            print("❌ Endpoint not found. The SSE endpoint may not be available.")
            return False
        else:
            print(f"❌ Connection failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Connection timed out")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        print("-" * 50)

def test_jira_api():
    """Test standard Jira API connection"""
    
    jira_base_url = os.getenv('JIRA_BASE_URL', 'https://jiramb.atlassian.net')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN') or os.getenv('JIRA_TOKEN')
    
    if not email or not api_token:
        print("❌ Missing credentials")
        return False
    
    # Create auth header
    auth_string = f"{email}:{api_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Accept': 'application/json'
    }
    
    print(f"\n🔗 Testing standard Jira API at: {jira_base_url}")
    
    try:
        # Test with myself endpoint
        test_url = f"{jira_base_url}/rest/api/3/myself"
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Successfully connected to Jira API")
            print(f"👤 Authenticated as: {user_data.get('displayName', 'Unknown')}")
            print(f"📧 Email: {user_data.get('emailAddress', 'Unknown')}")
            return True
        else:
            print(f"❌ Jira API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Jira API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MCP SSE Connection Test")
    print("=" * 50)
    
    # First test standard Jira API
    print("\n1️⃣ Testing Standard Jira API Connection")
    jira_success = test_jira_api()
    
    # Then test MCP SSE
    print("\n2️⃣ Testing MCP SSE Connection")
    sse_success = test_mcp_sse_connection()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Standard Jira API: {'✅ Success' if jira_success else '❌ Failed'}")
    print(f"MCP SSE Endpoint:  {'✅ Success' if sse_success else '❌ Failed'}")
    
    if not sse_success:
        print("\n💡 Note: The MCP SSE endpoint may require:")
        print("  - Special permissions or account type")
        print("  - Different authentication method")
        print("  - Access to be enabled by an administrator")
        print("  - A different URL structure for your Atlassian instance")