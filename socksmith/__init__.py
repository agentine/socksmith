"""socksmith — Modern drop-in replacement for PySocks."""

from __future__ import annotations

from socksmith._exceptions import (
    GeneralProxyError,
    HTTPError,
    ProxyConnectionError,
    ProxyError,
    SOCKS4Error,
    SOCKS5AuthError,
    SOCKS5Error,
)
from socksmith._globals import get_default_proxy, set_default_proxy
from socksmith._socket import create_connection, socksocket
from socksmith._types import ProxyType

__all__ = [
    "ProxyType",
    "SOCKS4",
    "SOCKS4A",
    "SOCKS5",
    "SOCKS5H",
    "HTTP",
    "socksocket",
    "set_default_proxy",
    "get_default_proxy",
    "setdefaultproxy",
    "create_connection",
    "ProxyError",
    "GeneralProxyError",
    "ProxyConnectionError",
    "SOCKS5AuthError",
    "SOCKS5Error",
    "SOCKS4Error",
    "HTTPError",
]

# Convenience aliases
SOCKS4 = ProxyType.SOCKS4
SOCKS4A = ProxyType.SOCKS4A
SOCKS5 = ProxyType.SOCKS5
SOCKS5H = ProxyType.SOCKS5H
HTTP = ProxyType.HTTP

# PySocks compat alias
setdefaultproxy = set_default_proxy
