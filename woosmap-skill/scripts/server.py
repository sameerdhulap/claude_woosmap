"""
HTTP-enabled MCP server for Web Claude deployment
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.sse import SseServerTransport
import uvicorn
import logging

# Import the MCP instance and tools
from core import mcp
import localities  # noqa
import distance  # noqa
import transit  # noqa

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Woosmap MCP Server", version="1.0.0")

# Enable CORS for web Claude
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://claude.ai",
        "https://*.claude.ai",
        "http://localhost:*",  # For local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Woosmap MCP Server",
        "status": "running",
        "version": "1.0.0",
        "transport": "SSE"
    }

@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {"status": "healthy"}

@app.get("/sse")
async def sse_endpoint():
    """
    SSE endpoint for MCP protocol over HTTP.
    This is what web Claude connects to.
    """
    logger.info("SSE connection initiated")
    async with SseServerTransport("/messages") as transport:
        await mcp.run(transport=transport)

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
