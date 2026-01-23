# Using Woosmap Skill with Web Claude (claude.ai)

Web Claude and Claude Desktop handle MCP servers differently. Here are your options:

## Understanding the Difference

- **Claude Desktop**: Runs MCP servers locally on your computer
- **Web Claude**: Can only connect to remotely hosted MCP servers via HTTP

## Option 1: Use a Hosted MCP Server (Recommended)

Deploy your Woosmap MCP server to a cloud service and connect it to web Claude.

### Step 1: Deploy the MCP Server

Deploy the scripts from your Woosmap skill to a hosting service that supports Python:

**Popular hosting options:**

#### A. Railway.app (Easiest)
1. Create account at [railway.app](https://railway.app)
2. Create new project → Deploy from GitHub
3. Upload your MCP server code
4. Add environment variable: `WOOSMAP_API_KEY=your-key-here`
5. Railway will give you a URL like `https://your-app.railway.app`

#### B. Heroku
1. Create Heroku account
2. Create new app
3. Deploy MCP server code
4. Configure environment variables in Settings → Config Vars
5. Use the app URL provided by Heroku

#### C. Google Cloud Run / AWS Lambda / Azure Functions
Deploy as a serverless function with HTTP transport.

### Step 2: Modify MCP Server for HTTP Transport

Your current MCP server uses `stdio` transport. For web Claude, you need HTTP transport.

Update `scripts/main.py`:

```python
from core import mcp

# Import tools
import localities
import distance
import transit

def main():
    # For web Claude, use HTTP transport instead of stdio
    mcp.run(transport="sse")  # Server-Sent Events over HTTP

if __name__ == "__main__":
    main()
```

Add a web server wrapper (create `scripts/server.py`):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.sse import SseServerTransport
from main import mcp
import uvicorn

app = FastAPI()

# Enable CORS for web Claude
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://claude.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/sse")
async def sse_endpoint():
    async with SseServerTransport("/messages") as transport:
        await mcp.run(transport=transport)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Update `scripts/pyproject.toml` to include FastAPI and uvicorn:

```toml
[project]
name = "woosmap"
version = "0.1.0"
description = "Woosmap MCP server"
requires-python = ">=3.10"
dependencies = [
    "debugpy>=1.8.19",
    "httpx>=0.28.1",
    "mcp[cli]>=1.25.0",
    "pillow>=12.1.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
]
```

### Step 3: Connect to Web Claude

1. Go to [claude.ai](https://claude.ai)
2. Click Settings → MCP Servers (or Integrations)
3. Click "Add MCP Server"
4. Enter your hosted URL: `https://your-app.railway.app/sse`
5. Name it "Woosmap"
6. Save

Now the Woosmap tools will be available in web Claude!

## Option 2: Use Claude Desktop Instead

If managing a hosted server is too complex, simply use Claude Desktop with the original skill package. Claude Desktop is specifically designed to run local MCP servers easily.

## Option 3: Request Anthropic Integration

If Woosmap becomes popular, you could request that Anthropic add native Woosmap integration to web Claude, similar to how they have integrated other services.

## Option 4: Simplified Skill (No MCP Server)

Create a web Claude-only skill that provides instructions for Claude to make HTTP requests directly:

### Create a simplified skill

```yaml
---
name: woosmap-web
description: Woosmap API integration for web Claude. Use when users need location services.
---

# Woosmap Integration for Web Claude

This skill enables Claude to use the Woosmap API directly via HTTP requests.

## Setup

Users need to provide their Woosmap API key when using this skill.

## Usage

When users request location services, ask them for their Woosmap API key if not provided, then make direct HTTP requests to the Woosmap API:

### Example: Search for places

```python
import httpx

async def search_places(api_key: str, query: str, lat: float, lng: float):
    url = "https://api.woosmap.com/localities/autocomplete"
    params = {
        "input": query,
        "location": f"{lat},{lng}",
        "key": api_key
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()
```

[Include more examples and API documentation]
```

**Limitations of this approach:**
- User must provide API key in each conversation
- No persistent authentication
- Less secure (API key in chat history)

## Comparison

| Feature | Claude Desktop | Web Claude (Hosted MCP) | Web Claude (Direct API) |
|---------|---------------|------------------------|------------------------|
| Setup complexity | Easy | Medium | Hard |
| API key security | Secure (local env) | Secure (server env) | Less secure (in chat) |
| Maintenance | None | Server maintenance | None |
| Cost | Free | Hosting costs | Free |
| Best for | Personal use | Team/production | Quick testing |

## Recommendation

- **Personal use**: Use Claude Desktop with the packaged skill
- **Team/production use**: Deploy hosted MCP server for web Claude  
- **Quick testing**: Use direct API approach temporarily

## Resources

- [MCP Server Deployment Guide](https://modelcontextprotocol.io/docs/deployment)
- [Woosmap API Documentation](https://developers.woosmap.com/)
- [FastMCP HTTP Transport](https://github.com/jlowin/fastmcp#http-transport)
