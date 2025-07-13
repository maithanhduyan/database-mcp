# -*- coding: utf-8 -*-
# File: app/mcp.py

from fastapi import APIRouter
from typing import Callable, Dict, Any, Optional, Union
from datetime import datetime, timezone
import json
from app.json_rpc import JsonRpcRequest, JsonRpcResponse, JsonRpcErrorResponse, create_success_response, create_error_response
from app.logger import get_logger
from app.db import execute_query


logger = get_logger(__name__)


router = APIRouter()


from typing import TypedDict

class ToolMeta(TypedDict):
    func: Callable
    description: str
    input_schema: dict

# Registry cho các tool MCP
TOOL_HANDLERS: Dict[str, ToolMeta] = {}

def register_tool(tool_name: str, description: str = "", input_schema: Optional[dict] = None, func: Optional[Callable] = None):
    """
    Có thể dùng như decorator hoặc hàm thường.
    Dùng: @register_tool("name", description=..., input_schema=...)
    """
    def decorator(f: Callable):
        TOOL_HANDLERS[tool_name] = {
            "func": f,
            "description": description,
            "input_schema": input_schema or {}
        }
        return f
    if func:
        return decorator(func)
    return decorator

async def handle_initialize(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Initialize method - MCP protocol initialization
    This is called when a client first connects to establish capabilities
    """
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "listChanged": False
            },
            "prompts": {
                "listChanged": False
            },
            "resources": {
                "subscribe": False,
                "listChanged": False
            },
            "logging": {}
        },
        "serverInfo": {
            "name": "embed-mcp",
            "version": "1.0.0"
        },
        "instructions": "MCP Server initialized successfully"
    }

async def handle_notifications_initialized(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Handle initialized notification from client
    This is a notification (no response expected) but we'll return empty for consistency
    """
    logger.info("Client initialization completed")
    return {
        "status": "acknowledged",
        "message": "Server ready for requests"
    }

async def handle_tools_list(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    List available tools - MCP standard method
    """
    tools = []
    for name, meta in TOOL_HANDLERS.items():
        tools.append({
            "name": name,
            "description": meta["description"],
            "inputSchema": meta["input_schema"]
        })
    return {"tools": tools}

@register_tool(
    "echo",
    description="Echoes back the provided message.",
    input_schema={
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Message to echo back"
            }
        },
        "required": ["message"]
    }
)
async def tool_echo(arguments: dict) -> dict:
    message = arguments.get("message", "")
    return {
        "content": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

@register_tool(
    "execute_query",
    description="Execute SQL SELECT query and return results.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL SELECT query to execute"
            },
            "params": {
                "type": "object",
                "description": "Query parameters (optional)",
                "default": {}
            }
        },
        "required": ["query"]
    }
)
async def tool_execute_query(arguments: dict) -> dict:
    query = arguments.get("query", "")
    params = arguments.get("params", {})
    
    if not query.strip().upper().startswith("SELECT"):
        return {
            "content": [
                {
                    "type": "text", 
                    "text": "Error: Only SELECT queries are allowed"
                }
            ]
        }
    
    try:
        results = execute_query(query, params)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Query executed successfully. Found {len(results)} rows."
                },
                {
                    "type": "text",
                    "text": json.dumps(results, indent=2, ensure_ascii=False)
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error executing query: {str(e)}"
                }
            ]
        }

async def handle_tools_call(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Call a tool - MCP standard method
    """
    logger.info("Handling 'tools/call' method")
    if not params or not isinstance(params, dict):
        return {"error": "Invalid parameters for tools/call"}

    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if not tool_name:
        return {"error": "Tool name is required"}

    meta = TOOL_HANDLERS.get(tool_name)
    if not meta:
        return {"error": f"Unknown tool: {tool_name}"}
    return await meta["func"](arguments)

@router.post("/")
async def handle_request(request: JsonRpcRequest) -> Union[JsonRpcResponse, JsonRpcErrorResponse]:
    """
    Handle MCP JSON-RPC requests
    """
    try:
        method = request.method
        params = request.params
        
        logger.info(f"Handling MCP request: {method}")
        
        # Direct method routing instead of registry
        if method == "initialize":
            result = await handle_initialize(params)
        elif method == "notifications/initialized":
            result = await handle_notifications_initialized(params)
        elif method == "tools/list":
            result = await handle_tools_list(params)
        elif method == "tools/call":
            result = await handle_tools_call(params)
        else:
            return create_error_response(
                "METHOD_NOT_FOUND",
                f"Method not found: {method}",
                request.id,
                None
            )
        
        return create_success_response(result, request.id)
        
    except Exception as e:
        logger.error(f"Error handling MCP request {request.method}: {e}")
        return create_error_response(
            "INTERNAL_ERROR",
            f"Internal error: {str(e)}",
            request.id,
            None
        )

