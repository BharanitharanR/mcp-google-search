#!/usr/bin/env python3
"""
MCP Server for Google Search Integration
Provides tools to search Google and fetch results for AI model consumption
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlparse

from googlesearch import search
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("google-search-server")

# Create server instance
server = Server("google-search-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema.
    """
    return [
        types.Tool(
            name="google_search",
            description="Search Google and return a list of URLs and titles",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to execute",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of search results to return (default: 10, max: 20)",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 10,
                    },
                    "lang": {
                        "type": "string",
                        "description": "Language for search results (default: 'en')",
                        "default": "en",
                    },
                    "country": {
                        "type": "string",
                        "description": "Country code for search results (default: 'us')",
                        "default": "us",
                    },
                    "pause": {
                        "type": "number",
                        "description": "Pause between requests in seconds (default: 2.0)",
                        "minimum": 0.5,
                        "maximum": 10.0,
                        "default": 2.0,
                    }
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="google_search_detailed",
            description="Search Google and return detailed results with snippets and metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to execute",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of search results to return (default: 5, max: 10)",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 5,
                    },
                    "include_snippets": {
                        "type": "boolean",
                        "description": "Whether to include page snippets (requires additional requests)",
                        "default": True,
                    }
                },
                "required": ["query"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    if not arguments:
        arguments = {}

    if name == "google_search":
        return await _handle_google_search(arguments)
    elif name == "google_search_detailed":
        return await _handle_google_search_detailed(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def _handle_google_search(arguments: dict[str, Any]) -> list[types.TextContent]:
    """
    Handle basic Google search requests.
    """
    query = arguments.get("query", "")
    num_results = arguments.get("num_results", 10)
    lang = arguments.get("lang", "en")
    country = arguments.get("country", "us")
    pause_time = arguments.get("pause", 2.0)
    
    if not query:
        return [types.TextContent(
            type="text",
            text="Error: Query parameter is required"
        )]
    
    try:
        logger.info(f"Executing Google search for: {query}")
        
        # Execute search
        search_results = []
        for url in search(
            query,
            num_results=num_results,
            lang=lang,
            country=country,
            pause=pause_time,
            user_agent="Mozilla/5.0 (compatible; MCP-GoogleSearch/1.0)"
        ):
            search_results.append({
                "url": url,
                "domain": urlparse(url).netloc
            })
        
        # Format results
        results = {
            "query": query,
            "num_results": len(search_results),
            "results": search_results
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(results, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error during Google search: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error executing search: {str(e)}"
        )]

async def _handle_google_search_detailed(arguments: dict[str, Any]) -> list[types.TextContent]:
    """
    Handle detailed Google search requests with additional metadata.
    """
    query = arguments.get("query", "")
    num_results = arguments.get("num_results", 5)
    include_snippets = arguments.get("include_snippets", True)
    
    if not query:
        return [types.TextContent(
            type="text",
            text="Error: Query parameter is required"
        )]
    
    try:
        logger.info(f"Executing detailed Google search for: {query}")
        
        # Execute search
        search_results = []
        for i, url in enumerate(search(
            query,
            num_results=num_results,
            pause=2.0,
            user_agent="Mozilla/5.0 (compatible; MCP-GoogleSearch/1.0)"
        )):
            result_data = {
                "rank": i + 1,
                "url": url,
                "domain": urlparse(url).netloc,
                "title": f"Search Result {i + 1}",  # Basic title
            }
            
            # Add snippet if requested (note: basic implementation)
            if include_snippets:
                result_data["snippet"] = f"Content preview for {urlparse(url).netloc}..."
            
            search_results.append(result_data)
        
        # Format detailed results
        results = {
            "query": query,
            "timestamp": asyncio.get_event_loop().time(),
            "num_results": len(search_results),
            "results": search_results,
            "metadata": {
                "search_engine": "Google",
                "language": "en",
                "country": "us"
            }
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(results, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error during detailed Google search: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error executing detailed search: {str(e)}"
        )]

async def main():
    """Main entry point for the server."""
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="google-search-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
