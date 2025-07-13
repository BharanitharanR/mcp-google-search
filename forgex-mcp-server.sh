#!/usr/bin/env bash
# google-search-mcp-server wrapper script
# This script allows the MCP server to be run with mcpo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python MCP server
exec python3 "$SCRIPT_DIR/forgex_mcp_server.py" "$@"
