# MCP Google Search Server

## Requirements

Create a `requirements.txt` file:

```txt
mcp>=1.0.0
googlesearch-python>=1.2.3
```

## Installation

### Option 1: Direct Installation (Recommended for mcpo)

1. Create the package structure:
```bash
mkdir google-search-mcp-server
cd google-search-mcp-server
```

2. Save the server code as `google_search_server.py`
3. Save the `pyproject.toml` file
4. Create a simple `README.md`

5. Install in development mode:
```bash
pip install -e .
```

### Option 2: Virtual Environment Installation

1. Create a virtual environment:
```bash
python -m venv mcp-google-search
source mcp-google-search/bin/activate  # On Windows: mcp-google-search\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage with mcpo

### Running with mcpo

Once installed, you can run your server with mcpo like this:

```bash
uvx mcpo --port 8000 -- google-search-mcp-server
```

Or if you want to specify a custom script:

```bash
uvx mcpo --port 8000 -- python google_search_server.py
```

### Alternative: Create a shell script wrapper

Create a file called `google-search-mcp-server` (no extension):

```bash
#!/bin/bash
python3 /path/to/your/google_search_server.py "$@"
```

Make it executable:
```bash
chmod +x google-search-mcp-server
```

Then use with mcpo:
```bash
uvx mcpo --port 8000 -- ./google-search-mcp-server
```

### Testing the Integration

1. Start the server with mcpo:
```bash
uvx mcpo --port 8000 -- google-search-mcp-server
```

2. Test the connection:
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

3. Test a search:
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "google_search",
      "arguments": {
        "query": "python programming",
        "num_results": 5
      }
    }
  }'
```

### Available Tools

The server provides two tools:

#### 1. `google_search`
Basic Google search that returns URLs and domains.

**Parameters:**
- `query` (required): Search query string
- `num_results` (optional): Number of results (1-20, default: 10)
- `lang` (optional): Language code (default: "en")
- `country` (optional): Country code (default: "us")
- `pause` (optional): Pause between requests in seconds (0.5-10.0, default: 2.0)

**Example Response:**
```json
{
  "query": "python programming",
  "num_results": 3,
  "results": [
    {
      "url": "https://www.python.org/",
      "domain": "www.python.org"
    },
    {
      "url": "https://docs.python.org/",
      "domain": "docs.python.org"
    }
  ]
}
```

#### 2. `google_search_detailed`
Detailed search with additional metadata and snippets.

**Parameters:**
- `query` (required): Search query string
- `num_results` (optional): Number of results (1-10, default: 5)
- `include_snippets` (optional): Include content snippets (default: true)

**Example Response:**
```json
{
  "query": "machine learning",
  "timestamp": 1234567890.123,
  "num_results": 2,
  "results": [
    {
      "rank": 1,
      "url": "https://example.com/ml",
      "domain": "example.com",
      "title": "Search Result 1",
      "snippet": "Content preview for example.com..."
    }
  ],
  "metadata": {
    "search_engine": "Google",
    "language": "en",
    "country": "us"
  }
}
```

## Integration with AI Models

The search results are returned as structured JSON that you can easily parse and feed to your AI model. Here's an example of how to use the results:

```python
import json

# Parse the search results
results = json.loads(search_response)

# Extract URLs for further processing
urls = [result["url"] for result in results["results"]]

# Extract domains for filtering
domains = [result["domain"] for result in results["results"]]

# Feed to your AI model
context = f"Search query: {results['query']}\n"
context += f"Found {results['num_results']} results:\n"
for i, result in enumerate(results["results"], 1):
    context += f"{i}. {result['url']}\n"
```

## Configuration

### Rate Limiting
The server includes built-in rate limiting with configurable pause times between requests to respect Google's terms of service. The default pause is 2 seconds.

### User Agent
The server uses a custom user agent string to identify itself as an MCP Google Search server.

### Error Handling
The server includes comprehensive error handling and logging for debugging purposes.

## Important Notes

1. **Rate Limiting**: Google may rate limit or block requests if you make too many searches too quickly. The server includes pause functionality to help mitigate this.

2. **Terms of Service**: Make sure your use complies with Google's Terms of Service.

3. **IP Blocking**: If you make too many requests, Google might temporarily block your IP address.

4. **Accuracy**: The `googlesearch-python` library provides basic search functionality. For more advanced features, consider using the official Google Search API.

## Troubleshooting

### Common Issues

1. **HTTP 429 (Too Many Requests)**: Increase the pause time between requests
2. **No results returned**: Check if your IP is blocked or if the query is valid
3. **Import errors**: Ensure all dependencies are installed correctly

### Debugging

Enable debug logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Extending the Server

You can extend this server by adding more tools:

- Web scraping tool to fetch page content
- URL validation tool
- Search result filtering tool
- Cache management for frequent queries
