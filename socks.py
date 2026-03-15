"""PySocks compatibility shim.

Re-exports socksmith's public API using PySocks-compatible names so that
``import socks`` works as a drop-in replacement.
"""

from __future__ import annotations

import socksmith
from socksmith._types import ProxyType

# Re-export classes and functions
socksocket = socksmith.socksocket
set_default_proxy = socksmith.set_default_proxy
get_default_proxy = socksmith.get_default_proxy
create_connection = socksmith.create_connection

# Re-export exceptions
ProxyError = socksmith.ProxyError
GeneralProxyError = socksmith.GeneralProxyError
ProxyConnectionError = socksmith.ProxyConnectionError
SOCKS5AuthError = socksmith.SOCKS5AuthError
SOCKS5Error = socksmith.SOCKS5Error
SOCKS4Error = socksmith.SOCKS4Error
HTTPError = socksmith.HTTPError

# PySocks-compatible constants
PROXY_TYPE_SOCKS4 = ProxyType.SOCKS4
PROXY_TYPE_SOCKS5 = ProxyType.SOCKS5
PROXY_TYPE_HTTP = ProxyType.HTTP

# Short aliases (also present in PySocks)
SOCKS4 = ProxyType.SOCKS4
SOCKS5 = ProxyType.SOCKS5
HTTP = ProxyType.HTTP

# Extended types (socksmith additions)
SOCKS4A = ProxyType.SOCKS4A
SOCKS5H = ProxyType.SOCKS5H
PROXY_TYPE_SOCKS4A = ProxyType.SOCKS4A
PROXY_TYPE_SOCKS5H = ProxyType.SOCKS5H

PROXY_TYPES: dict[ProxyType, str] = {
    ProxyType.SOCKS4: "SOCKS4",
    ProxyType.SOCKS4A: "SOCKS4A",
    ProxyType.SOCKS5: "SOCKS5",
    ProxyType.SOCKS5H: "SOCKS5H",
    ProxyType.HTTP: "HTTP",
}

DEFAULT_PORTS: dict[ProxyType, int] = {
    ProxyType.SOCKS4: 1080,
    ProxyType.SOCKS4A: 1080,
    ProxyType.SOCKS5: 1080,
    ProxyType.SOCKS5H: 1080,
    ProxyType.HTTP: 8080,
}

# PySocks compat alias
setdefaultproxy = set_default_proxy

__all__ = [
    "PROXY_TYPE_SOCKS4",
    "PROXY_TYPE_SOCKS5",
    "PROXY_TYPE_HTTP",
    "PROXY_TYPE_SOCKS4A",
    "PROXY_TYPE_SOCKS5H",
    "SOCKS4",
    "SOCKS5",
    "HTTP",
    "SOCKS4A",
    "SOCKS5H",
    "PROXY_TYPES",
    "DEFAULT_PORTS",
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
