"""Internal utilities."""

from __future__ import annotations

import socket

from socksmith._exceptions import GeneralProxyError


def recvall(sock: socket.socket, count: int) -> bytes:
    """Read exactly *count* bytes from *sock*."""
    data = bytearray()
    while len(data) < count:
        chunk = sock.recv(count - len(data))
        if not chunk:
            raise GeneralProxyError("Connection closed unexpectedly during proxy handshake")
        data.extend(chunk)
    return bytes(data)
