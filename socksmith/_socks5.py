"""SOCKS5 and SOCKS5h protocol client."""

from __future__ import annotations

import socket
import struct

from socksmith._exceptions import GeneralProxyError, SOCKS5AuthError, SOCKS5Error
from socksmith._types import ProxyType
from socksmith._utils import recvall

__all__ = ["Socks5Client"]

# Auth methods
_AUTH_NONE = 0x00
_AUTH_USERNAME_PASSWORD = 0x02
_AUTH_NO_ACCEPTABLE = 0xFF

# Reply codes (RFC 1928)
_SOCKS5_ERRORS: dict[int, str] = {
    0x01: "General SOCKS server failure",
    0x02: "Connection not allowed by ruleset",
    0x03: "Network unreachable",
    0x04: "Host unreachable",
    0x05: "Connection refused",
    0x06: "TTL expired",
    0x07: "Command not supported",
    0x08: "Address type not supported",
}

# Address types
_ATYP_IPV4 = 0x01
_ATYP_DOMAIN = 0x03
_ATYP_IPV6 = 0x04


class Socks5Client:
    """SOCKS5/SOCKS5h CONNECT client."""

    @staticmethod
    def connect(
        sock: socket.socket,
        dest_addr: str,
        dest_port: int,
        proxy_type: ProxyType = ProxyType.SOCKS5,
        username: str | None = None,
        password: str | None = None,
    ) -> tuple[str, int]:
        """Perform a SOCKS5/5h CONNECT handshake.

        Returns the bound address ``(addr, port)`` from the proxy reply.
        """
        # Step 1: Greeting
        if username and password:
            methods = bytes([_AUTH_NONE, _AUTH_USERNAME_PASSWORD])
        else:
            methods = bytes([_AUTH_NONE])

        sock.sendall(struct.pack("!BB", 0x05, len(methods)) + methods)

        # Step 2: Server selects auth method
        reply = recvall(sock, 2)
        ver, method = struct.unpack("!BB", reply)

        if ver != 0x05:
            raise GeneralProxyError(f"Unexpected SOCKS version in greeting reply: {ver}")

        if method == _AUTH_NO_ACCEPTABLE:
            raise SOCKS5AuthError("No acceptable authentication methods")

        if method == _AUTH_USERNAME_PASSWORD:
            if not username or not password:
                raise SOCKS5AuthError("Server requires username/password authentication")
            _do_username_password_auth(sock, username, password)
        elif method != _AUTH_NONE:
            raise SOCKS5AuthError(f"Unsupported authentication method: 0x{method:02X}")

        # Step 3: CONNECT request
        if proxy_type == ProxyType.SOCKS5H:
            # Remote DNS: send hostname
            addr_bytes = dest_addr.encode("ascii")
            addr_payload = struct.pack("!BB", _ATYP_DOMAIN, len(addr_bytes)) + addr_bytes
        else:
            # Local DNS: resolve and send IP
            try:
                addr_info = socket.getaddrinfo(dest_addr, dest_port)
            except (socket.gaierror, OSError) as exc:
                raise GeneralProxyError(f"Failed to resolve {dest_addr!r}") from exc

            ipv4 = [ai for ai in addr_info if ai[0] == socket.AF_INET]
            ipv6 = [ai for ai in addr_info if ai[0] == socket.AF_INET6]

            if ipv4:
                host4: str = ipv4[0][4][0]  # type: ignore[assignment]
                ip_bytes = socket.inet_aton(host4)
                addr_payload = struct.pack("!B", _ATYP_IPV4) + ip_bytes
            elif ipv6:
                host6: str = ipv6[0][4][0]  # type: ignore[assignment]
                ip_bytes = socket.inet_pton(socket.AF_INET6, host6)
                addr_payload = struct.pack("!B", _ATYP_IPV6) + ip_bytes
            else:
                raise GeneralProxyError(f"No usable address for {dest_addr!r}")

        request = (
            struct.pack("!BBB", 0x05, 0x01, 0x00) + addr_payload + struct.pack("!H", dest_port)
        )
        sock.sendall(request)

        # Step 4: Parse reply
        reply_header = recvall(sock, 3)
        ver, rep, _ = struct.unpack("!BBB", reply_header)

        if ver != 0x05:
            raise GeneralProxyError(f"Unexpected SOCKS version in connect reply: {ver}")

        if rep != 0x00:
            error_msg = _SOCKS5_ERRORS.get(rep, f"Unknown SOCKS5 error code: 0x{rep:02X}")
            raise SOCKS5Error(error_msg)

        # Read bound address
        atyp = recvall(sock, 1)[0]

        if atyp == _ATYP_IPV4:
            bound_addr = socket.inet_ntoa(recvall(sock, 4))
        elif atyp == _ATYP_IPV6:
            bound_addr = socket.inet_ntop(socket.AF_INET6, recvall(sock, 16))
        elif atyp == _ATYP_DOMAIN:
            length = recvall(sock, 1)[0]
            bound_addr = recvall(sock, length).decode("ascii")
        else:
            raise GeneralProxyError(f"Unsupported address type: 0x{atyp:02X}")

        bound_port = struct.unpack("!H", recvall(sock, 2))[0]
        return bound_addr, bound_port


def _do_username_password_auth(sock: socket.socket, username: str, password: str) -> None:
    """Perform RFC 1929 username/password sub-negotiation."""
    user_bytes = username.encode("utf-8")
    pass_bytes = password.encode("utf-8")

    if len(user_bytes) > 255 or len(pass_bytes) > 255:
        raise SOCKS5AuthError("Username or password exceeds 255 bytes")

    auth_request = (
        struct.pack("!BB", 0x01, len(user_bytes))
        + user_bytes
        + struct.pack("!B", len(pass_bytes))
        + pass_bytes
    )
    sock.sendall(auth_request)

    reply = recvall(sock, 2)
    _, status = struct.unpack("!BB", reply)

    if status != 0x00:
        raise SOCKS5AuthError("SOCKS5 username/password authentication failed")
