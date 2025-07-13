# Test MCP database tools
import requests
import json

def call_mcp_tool(tool_name, arguments=None):
    url = "http://localhost:8000/mcp/"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    response = requests.post(url, json=payload)
    result = response.json()
    
    if "result" in result and "content" in result["result"]:
        for content in result["result"]["content"]:
            print(content["text"])
    else:
        print(json.dumps(result, indent=2))

print("=== Testing SELECT queries ===")
call_mcp_tool("execute_query", {"query": "SELECT * FROM users"})

print("\n=== Testing SELECT products ===")
call_mcp_tool("execute_query", {"query": "SELECT * FROM products"})

print("\n=== Testing echo ===")
call_mcp_tool("echo", {"message": "MCP database tools are working perfectly!"})
