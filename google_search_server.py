#!/usr/bin/env python3
"""
MCP Server for Forgex App Ingestion
Forwards structured app creation payloads to the Forgex API/service
"""

import argparse
import asyncio
import json
import logging
import sys
from typing import Any

import httpx
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("forgex-ingestor-server")

# Initialize MCP server
server = Server("forgex-ingestor-server")

# Your Forgex service endpoint
FORGEX_API_URL = "http://localhost:8081/graph/process"  # Change as per your API

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    Expose the Forgex ingestor tool
    """
    return [
        types.Tool(
            name="create_app_with_forgex",
            description="Create an app using Forgex from a structured payload",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_spec": {
                        "type": "object",
                        "description": "The structured JSON payload representing the app (entities, edges, rules, etc.)"
                    }
                },
                "required": ["app_spec"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent]:
    """
    Handle incoming tool call
    """
    if name == "create_app_with_forgex":
        return await _handle_forgex_create(arguments)
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def _handle_forgex_create(arguments: dict[str, Any]) -> list[types.TextContent]:
    """
    Forward the app_spec payload to Forgex
    """
    app_spec = arguments.get("app_spec")
    if not app_spec:
        return [types.TextContent(
            type="text",
            text="Error: 'app_spec' is required."
        )]

    try:
        logger.info(f"Sending app spec to Forgex...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                FORGEX_API_URL,
                json=app_spec,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
        response.raise_for_status()
        result = response.json()

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    except Exception as e:
        logger.error(f"Forgex ingestion failed: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error while sending data to Forgex: {str(e)}"
        )]

async def run_server():
    """
    Entry point for MCP server
    """
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="forgex-ingestor-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def main():
    parser = argparse.ArgumentParser(description="Forgex Ingestor MCP Server")
    parser.add_argument("--version", action="version", version="forgex-ingestor-server 0.1.0")
    args = parser.parse_args()

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Shutting down Forgex Ingestor MCP server")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
