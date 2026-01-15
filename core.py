import sys
import os
import logging
import debugpy
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# -------------------------------------------------
# Logging / Debug
# -------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)

if os.getenv("MCP_DEBUG") == "1":
    debugpy.listen(("127.0.0.1", 5678))

# -------------------------------------------------
# MCP server
# -------------------------------------------------
mcp = FastMCP("woosmapmcp")

# -------------------------------------------------
# Constants
# -------------------------------------------------
WOOSMAP_API_BASE = "https://api.woosmap.com"
USER_AGENT = "woosmapmcp-app/1.0"
REF_ORIGIN = "https://www.woosmap.com"
API_KEY = os.getenv("WOOSMAP_API_KEY", "")


# -------------------------------------------------
# HTTP helper
# -------------------------------------------------
async def make_woosmap_request(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    headers = {
        "User-Agent": USER_AGENT,
        "Origin": REF_ORIGIN,
    }
    params["key"] = API_KEY

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(
                f"{WOOSMAP_API_BASE}/{endpoint}",
                headers=headers,
                params=params,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            logger.exception("Woosmap API request failed")
            return {}


@mcp.tool()
async def health_check():
    """
    Check the health of the service.
    Returns:
        _type_: _description_
    """
    return {"result": {"status": "ok"}}
