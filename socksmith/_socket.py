"""socksocket — proxy-aware socket subclass."""

from __future__ import annotations

import socket
from typing import Any

from socksmith._exceptions import GeneralProxyError
from socksmith._globals import ProxyConfig, get_default_proxy
from socksmith._http import HttpConnectClient
from socksmith._socks4 import Socks4Client
from socksmith._socks5 import Socks5Client
from socksmith._types import ProxyType

__all__ = ["socksocket", "create_connection"]


class socksocket(socket.socket):  # noqa: N801
    """A socket subclass that connects through a SOCKS or HTTP proxy."""

    def __init__(
        self,
        family: socket.AddressFamily = socket.AF_INET,
        type: socket.SocketKind = socket.SOCK_STREAM,
        proto: int = 0,
        fileno: int | None = None,
    ) -> None:
        super().__init__(family, type, proto, fileno)
        self._proxy: ProxyConfig = (None, None, None, True, None, None)

    def set_proxy(
        self,
        proxy_type: ProxyType | None = None,
        addr: str | None = None,
        port: int | None = None,
        rdns: bool = True,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Configure the proxy for this socket instance."""
        self._proxy = (proxy_type, addr, port, rdns, username, password)

    # PySocks compat alias
    setproxy = set_proxy

    def _get_proxy(self) -> ProxyConfig:
        """Return instance proxy if set, otherwise module default."""
        if self._proxy[0] is not None:
            return self._proxy
        return get_default_proxy()

    def connect(self, dest_pair: tuple[str, int] | Any) -> None:
        """Connect through the configured proxy."""
        dest_addr: str = dest_pair[0]
        dest_port: int = dest_pair[1]
        proxy_type, proxy_addr, proxy_port, rdns, username, password = self._get_proxy()

        if proxy_type is None:
            super().connect((dest_addr, dest_port))
            return

        if proxy_addr is None:
            raise GeneralProxyError("Proxy address not set")

        # Default port
        if proxy_port is None:
            proxy_port = 8080 if proxy_type == ProxyType.HTTP else 1080

        # Connect to proxy server
        super().connect((proxy_addr, proxy_port))

        # Handle rdns flag
        effective_type = proxy_type
        if rdns:
            if proxy_type == ProxyType.SOCKS4:
                effective_type = ProxyType.SOCKS4A
            elif proxy_type == ProxyType.SOCKS5:
                effective_type = ProxyType.SOCKS5H

        # Dispatch handshake
        if effective_type in (ProxyType.SOCKS4, ProxyType.SOCKS4A):
            Socks4Client.connect(
                self,
                dest_addr=dest_addr,
                dest_port=dest_port,
                proxy_type=effective_type,
                username=username,
            )
        elif effective_type in (ProxyType.SOCKS5, ProxyType.SOCKS5H):
            Socks5Client.connect(
                self,
                dest_addr=dest_addr,
                dest_port=dest_port,
                proxy_type=effective_type,
                username=username,
                password=password,
            )
        elif effective_type == ProxyType.HTTP:
            HttpConnectClient.connect(
                self,
                dest_addr=dest_addr,
                dest_port=dest_port,
                username=username,
                password=password,
            )
        else:
            raise GeneralProxyError(f"Unsupported proxy type: {effective_type!r}")

    def connect_ex(self, dest_pair: tuple[str, int] | Any) -> int:
        """Connect through proxy, returning error code instead of raising."""
        try:
            self.connect(dest_pair)
            return 0
        except OSError as exc:
            return exc.errno or -1


def create_connection(
    dest_pair: tuple[str, int],
    timeout: float | None = None,
    source_address: tuple[str, int] | None = None,
    proxy_type: ProxyType | None = None,
    proxy_addr: str | None = None,
    proxy_port: int | None = None,
    proxy_rdns: bool = True,
    proxy_username: str | None = None,
    proxy_password: str | None = None,
) -> socksocket:
    """Create a connected socksocket, similar to ``socket.create_connection``."""
    sock = socksocket()

    if timeout is not None:
        sock.settimeout(timeout)

    if source_address is not None:
        sock.bind(source_address)

    if proxy_type is not None:
        sock.set_proxy(
            proxy_type, proxy_addr, proxy_port, proxy_rdns, proxy_username, proxy_password
        )

    sock.connect(dest_pair)
    return sock
