import sys
import os
import logging
import debugpy
from typing import Any, Dict

import httpx
from mcp.server.fastmcp import FastMCP

from exceptions import (
    WoosmapError,
    WoosmapAPIError,
    WoosmapAuthError,
    WoosmapRateLimitError,
    WoosmapNotFoundError,
    WoosmapBadRequestError,
    WoosmapNetworkError,
    WoosmapTimeoutError,
    WoosmapServerError,
)

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

# if not API_KEY:
#     raise WoosmapAuthError(
#         "WOOSMAP_API_KEY environment variable is not set. "
#         "Please set it to your Woosmap API key."
#     )


# -------------------------------------------------
# HTTP helper
# -------------------------------------------------
async def make_woosmap_request(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    Make an HTTP request to the Woosmap API.

    Args:
        endpoint: API endpoint path (e.g., "localities/nearby")
        params: Query parameters to send with the request

    Returns:
        Parsed JSON response from the API

    Raises:
        WoosmapAuthError: Invalid or missing API key (401/403)
        WoosmapBadRequestError: Invalid request parameters (400)
        WoosmapNotFoundError: Resource not found (404)
        WoosmapRateLimitError: Rate limit exceeded (429)
        WoosmapServerError: Server-side error (5xx)
        WoosmapTimeoutError: Request timed out
        WoosmapNetworkError: Network connectivity issues
        WoosmapAPIError: Other API errors
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Origin": REF_ORIGIN,
    }
    params["key"] = API_KEY

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{WOOSMAP_API_BASE}/{endpoint}",
                headers=headers,
                params=params,
            )

            # Handle HTTP status codes
            if resp.status_code == 400:
                raise WoosmapBadRequestError(
                    f"Bad request: {resp.text}",
                    details={"status_code": 400, "endpoint": endpoint},
                )
            elif resp.status_code == 401:
                raise WoosmapAuthError(
                    "Invalid API key",
                    details={"status_code": 401, "endpoint": endpoint},
                )
            elif resp.status_code == 403:
                raise WoosmapAuthError(
                    "API key not authorized for this endpoint",
                    details={"status_code": 403, "endpoint": endpoint},
                )
            elif resp.status_code == 404:
                raise WoosmapNotFoundError(
                    f"Resource not found: {endpoint}",
                    details={"status_code": 404, "endpoint": endpoint},
                )
            elif resp.status_code == 429:
                raise WoosmapRateLimitError(
                    "Rate limit exceeded. Please try again later.",
                    details={"status_code": 429, "endpoint": endpoint},
                )
            elif 500 <= resp.status_code < 600:
                raise WoosmapServerError(
                    f"Server error: {resp.status_code}",
                    details={"status_code": resp.status_code, "endpoint": endpoint},
                )

            resp.raise_for_status()
            return resp.json()

    except httpx.TimeoutException as e:
        logger.error(f"Request to {endpoint} timed out: {e}")
        raise WoosmapTimeoutError(
            "Request timed out after 30 seconds",
            details={"endpoint": endpoint},
        ) from e

    except httpx.ConnectError as e:
        logger.error(f"Connection error to {endpoint}: {e}")
        raise WoosmapNetworkError(
            f"Failed to connect to Woosmap API: {e}",
            details={"endpoint": endpoint},
        ) from e

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from {endpoint}: {e}")
        raise WoosmapAPIError(
            f"HTTP error: {e.response.status_code}",
            details={"status_code": e.response.status_code, "endpoint": endpoint},
        ) from e

    except WoosmapError:
        # Re-raise our custom exceptions
        raise

    except Exception as e:
        logger.exception(f"Unexpected error during request to {endpoint}")
        raise WoosmapAPIError(
            f"Unexpected error: {str(e)}",
            details={"endpoint": endpoint, "error_type": type(e).__name__},
        ) from e


@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """
    Check the health of the service.
    Returns:
        _type_: _description_
    """
    return {"result": {"status": "ok"}}
