# Forgex Ingestor MCP Server

**MCP (Machine Control Protocol) server that forwards structured app creation payloads to the Forgex API.**

This server exposes a tool (`create_app_with_forgex`) via MCP that allows structured JSON payloads—describing applications—to be ingested by the Forgex backend.

## 🧩 Features

* MCP-compliant server using the `mcp` Python library
* Exposes a tool to create apps from structured payloads
* Forwards data to a configurable Forgex API endpoint
* Logs activity and errors for monitoring and debugging

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* A running Forgex API endpoint (default: `http://localhost:8081/graph/process`)

### Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/your-org/forgex-ingestor-server.git
cd forgex-ingestor-server
pip install -r requirements.txt
```

### Running the Server

```bash
python forgex_ingestor_server.py
```

To check version:

```bash
python forgex_ingestor_server.py --version
```

## 🔌 Tool Interface

### Tool Name: `create_app_with_forgex`

#### Description

Create an app using Forgex from a structured payload.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "app_spec": {
      "type": "object",
      "description": "The structured JSON payload representing the app (entities, edges, rules, etc.)"
    }
  },
  "required": ["app_spec"]
}
```

### Example Payload

```json
{
  "app_spec": {
    "entities": [...],
    "edges": [...],
    "rules": [...]
  }
}
```

## 🛠 Configuration

Update the `FORGEX_API_URL` in the script if your Forgex API endpoint differs:

```python
FORGEX_API_URL = "http://localhost:8081/graph/process"
```

## 📝 Logging

Logs are written to stdout with the logger named `forgex-ingestor-server`.

## 📁 Project Structure

```
forgex_ingestor_server.py     # Main server implementation
README.md                     # This file
requirements.txt              # Python dependencies
```

## 🧪 Development & Debugging

To debug requests/responses or extend the tool list, modify:

* `handle_list_tools()` — to expose new tools
* `_handle_forgex_create()` — to customize how payloads are processed

## 🛡️ License

MIT or your preferred license.

