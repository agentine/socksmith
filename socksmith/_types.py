"""Proxy type definitions."""

from __future__ import annotations

from enum import IntEnum

__all__ = ["ProxyType"]


class ProxyType(IntEnum):
    """Supported proxy types.

    Values for SOCKS4, SOCKS5, and HTTP match PySocks for backwards compatibility.
    """

    SOCKS4 = 1
    SOCKS5 = 2
    HTTP = 3
    SOCKS4A = 4
    SOCKS5H = 5
