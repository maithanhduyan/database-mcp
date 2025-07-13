# -*- coding: utf-8 -*-
# File: test_mcp_tools.py
"""
Test script để kiểm tra các MCP tools mới
"""

import requests
import json

BASE_URL = "http://localhost:8000/mcp/"

def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """Call MCP tool via HTTP"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    response = requests.post(BASE_URL, json=payload)
    return response.json()

def list_tools() -> dict:
    """List available MCP tools"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    response = requests.post(BASE_URL, json=payload)
    return response.json()

def test_all_tools():
    """Test all new MCP tools"""
    
    print("=== Available Tools ===")
    tools_response = list_tools()
    tools = tools_response.get("result", {}).get("tools", [])
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")
    
    print("\n=== Testing get_database_info ===")
    result = call_mcp_tool("get_database_info", {})
    print(json.dumps(result, indent=2))
    
    print("\n=== Testing get_table_info (all tables) ===")
    result = call_mcp_tool("get_table_info", {})
    print(json.dumps(result, indent=2))
    
    print("\n=== Testing get_table_info (users table) ===")
    result = call_mcp_tool("get_table_info", {"table_name": "users"})
    print(json.dumps(result, indent=2))
    
    print("\n=== Testing execute_command (INSERT) ===")
    result = call_mcp_tool("execute_command", {
        "query": "INSERT INTO users (name, email) VALUES ('Alice Johnson', 'alice@example.com')"
    })
    print(json.dumps(result, indent=2))
    
    print("\n=== Testing execute_query (SELECT) ===")
    result = call_mcp_tool("execute_query", {
        "query": "SELECT * FROM users WHERE name LIKE '%Alice%'"
    })
    print(json.dumps(result, indent=2))
    
    print("\n=== Testing execute_transaction ===")
    result = call_mcp_tool("execute_transaction", {
        "queries": [
            {"query": "INSERT INTO users (name, email) VALUES ('Bob Smith', 'bob@example.com')"},
            {"query": "INSERT INTO users (name, email) VALUES ('Carol White', 'carol@example.com')"}
        ]
    })
    print(json.dumps(result, indent=2))
    
    print("\n=== Final SELECT to see all users ===")
    result = call_mcp_tool("execute_query", {
        "query": "SELECT * FROM users ORDER BY name"
    })
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_all_tools()
