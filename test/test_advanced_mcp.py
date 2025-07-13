# -*- coding: utf-8 -*-
# Test advanced MCP operations

import requests
import json

BASE_URL = "http://localhost:8000/mcp/"

def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
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

def test_advanced_operations():
    print("=== Testing CREATE TABLE ===")
    result = call_mcp_tool("execute_command", {
        "query": """
        CREATE TABLE products (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10,2),
            category VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    })
    print(json.dumps(result, indent=2))
    
    print("\n=== Testing UPDATE operation ===")
    result = call_mcp_tool("execute_command", {
        "query": "UPDATE users SET name = 'Alice Johnson Updated' WHERE email = 'alice@example.com'"
    })
    print(json.dumps(result, indent=2))
    
    print("\n=== Testing Complex Transaction ===")
    result = call_mcp_tool("execute_transaction", {
        "queries": [
            {"query": "INSERT INTO products (name, price, category) VALUES ('Laptop', 999.99, 'Electronics')"},
            {"query": "INSERT INTO products (name, price, category) VALUES ('Phone', 699.99, 'Electronics')"},
            {"query": "INSERT INTO products (name, price, category) VALUES ('Book', 29.99, 'Education')"}
        ]
    })
    print(json.dumps(result, indent=2))
    
    print("\n=== Testing JOIN Query ===")
    result = call_mcp_tool("execute_query", {
        "query": """
        SELECT 
            users.name as user_name,
            users.email,
            products.name as product_name,
            products.price
        FROM users 
        CROSS JOIN products 
        WHERE products.category = 'Electronics'
        LIMIT 5
        """
    })
    print(json.dumps(result, indent=2))
    
    print("\n=== Testing Products Table Info ===")
    result = call_mcp_tool("get_table_info", {"table_name": "products"})
    print(json.dumps(result, indent=2))
    
    print("\n=== Testing DELETE operation ===") 
    result = call_mcp_tool("execute_command", {
        "query": "DELETE FROM products WHERE price < 50"
    })
    print(json.dumps(result, indent=2))
    
    print("\n=== Testing Final Database State ===")
    result = call_mcp_tool("get_database_info", {})
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_advanced_operations()
