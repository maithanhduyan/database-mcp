# Test MCP with authentication
import requests
import json

BASE_URL = "http://localhost:8000/mcp/"
HEADERS = {"MCP_API_KEY": "mcp-api-key-2025-super-secure-token"}

def test_mcp_with_auth():
    print("=== Testing MCP Authentication ===")
    
    # Test tools/list
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    print(f"Tools list status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        tools = result.get("result", {}).get("tools", [])
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
    
    # Test database info
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "get_database_info",
            "arguments": {}
        }
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    print(f"\nDatabase info status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("Database info retrieved successfully!")
        content = result.get("result", {}).get("content", [])
        for item in content:
            print(item.get("text", ""))
    
    # Test echo
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "echo",
            "arguments": {"message": "MCP_API_KEY authentication is working!"}
        }
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    print(f"\nEcho status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        content = result.get("result", {}).get("content", [])
        for item in content:
            print(f"Echo response: {item.get('text', '')}")

if __name__ == "__main__":
    test_mcp_with_auth()
