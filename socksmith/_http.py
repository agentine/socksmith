"""HTTP CONNECT proxy client."""

from __future__ import annotations

import base64
import socket

from socksmith._exceptions import GeneralProxyError, HTTPError

__all__ = ["HttpConnectClient"]


class HttpConnectClient:
    """HTTP CONNECT tunneling client."""

    @staticmethod
    def connect(
        sock: socket.socket,
        dest_addr: str,
        dest_port: int,
        username: str | None = None,
        password: str | None = None,
    ) -> tuple[str, int]:
        """Perform an HTTP CONNECT handshake.

        Returns ``(dest_addr, dest_port)`` on success.
        """
        host_header = f"{dest_addr}:{dest_port}"

        lines = [
            f"CONNECT {host_header} HTTP/1.1",
            f"Host: {host_header}",
        ]

        if username and password:
            credentials = base64.b64encode(
                f"{username}:{password}".encode()
            ).decode("ascii")
            lines.append(f"Proxy-Authorization: Basic {credentials}")

        request = "\r\n".join(lines) + "\r\n\r\n"
        sock.sendall(request.encode("ascii"))

        # Read HTTP response headers
        response = _read_http_response(sock)

        # Parse status line
        first_line = response.split("\r\n")[0] if "\r\n" in response else response.split("\n")[0]
        parts = first_line.split(" ", 2)

        if len(parts) < 2:
            raise GeneralProxyError(f"Malformed HTTP response: {first_line!r}")

        try:
            status_code = int(parts[1])
        except ValueError as exc:
            raise GeneralProxyError(f"Invalid HTTP status code: {parts[1]!r}") from exc

        if status_code != 200:
            reason = parts[2] if len(parts) > 2 else "Unknown"
            raise HTTPError(f"HTTP CONNECT failed: {status_code} {reason}")

        return dest_addr, dest_port


def _read_http_response(sock: socket.socket) -> str:
    """Read HTTP response headers until blank line."""
    data = bytearray()
    while True:
        byte = sock.recv(1)
        if not byte:
            raise GeneralProxyError("Connection closed during HTTP CONNECT response")
        data.extend(byte)
        if data.endswith(b"\r\n\r\n"):
            break
        if len(data) > 65536:
            raise GeneralProxyError("HTTP response headers too large")
    return data.decode("ascii", errors="replace")
