"""Exception hierarchy for socksmith.

All exception names match the PySocks public API exactly.
"""

from __future__ import annotations

__all__ = [
    "ProxyError",
    "GeneralProxyError",
    "ProxyConnectionError",
    "SOCKS5AuthError",
    "SOCKS5Error",
    "SOCKS4Error",
    "HTTPError",
]


class ProxyError(OSError):
    """Base exception for all proxy-related errors."""

    def __init__(self, msg: str, socket_err: OSError | None = None) -> None:
        self.msg = msg
        self.socket_err = socket_err
        super().__init__(msg)


class GeneralProxyError(ProxyError):
    """General proxy failure."""


class ProxyConnectionError(ProxyError):
    """Failed to connect to the proxy server."""


class SOCKS5AuthError(ProxyError):
    """SOCKS5 authentication failure."""


class SOCKS5Error(ProxyError):
    """SOCKS5 protocol error."""


class SOCKS4Error(ProxyError):
    """SOCKS4 protocol error."""


class HTTPError(ProxyError):
    """HTTP CONNECT proxy error."""
