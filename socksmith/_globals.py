"""Module-level default proxy state."""

from __future__ import annotations

import threading

from socksmith._types import ProxyType

__all__ = ["set_default_proxy", "get_default_proxy"]

ProxyConfig = tuple[ProxyType | None, str | None, int | None, bool, str | None, str | None]

_lock = threading.Lock()
_default_proxy: ProxyConfig = (None, None, None, True, None, None)


def set_default_proxy(
    proxy_type: ProxyType | None = None,
    addr: str | None = None,
    port: int | None = None,
    rdns: bool = True,
    username: str | None = None,
    password: str | None = None,
) -> None:
    """Set the module-level default proxy configuration."""
    global _default_proxy
    with _lock:
        _default_proxy = (proxy_type, addr, port, rdns, username, password)


def get_default_proxy() -> ProxyConfig:
    """Return the current default proxy configuration tuple."""
    with _lock:
        return _default_proxy
