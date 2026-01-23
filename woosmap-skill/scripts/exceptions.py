"""
Custom exceptions for Woosmap MCP server.
"""


class WoosmapError(Exception):
    """Base exception for all Woosmap-related errors."""

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self):
        """Convert exception to dictionary for MCP response."""
        return {
            "error": self.message,
            "error_type": self.__class__.__name__,
            **self.details,
        }


class WoosmapAPIError(WoosmapError):
    """General API error from Woosmap service."""

    pass


class WoosmapAuthError(WoosmapError):
    """Authentication/authorization error - invalid or missing API key."""

    pass


class WoosmapRateLimitError(WoosmapError):
    """Rate limit exceeded error."""

    pass


class WoosmapNotFoundError(WoosmapError):
    """Resource not found error."""

    pass


class WoosmapBadRequestError(WoosmapError):
    """Bad request error - invalid parameters."""

    pass


class WoosmapNetworkError(WoosmapError):
    """Network connectivity error."""

    pass


class WoosmapTimeoutError(WoosmapError):
    """Request timeout error."""

    pass


class WoosmapServerError(WoosmapError):
    """Server-side error (5xx responses)."""

    pass
