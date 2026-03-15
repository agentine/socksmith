"""SOCKS4 and SOCKS4a protocol client."""

from __future__ import annotations

import socket
import struct

from socksmith._exceptions import GeneralProxyError, SOCKS4Error
from socksmith._types import ProxyType
from socksmith._utils import recvall

__all__ = ["Socks4Client"]

_SOCKS4_ERRORS: dict[int, str] = {
    0x5B: "Request rejected or failed",
    0x5C: "Request rejected: SOCKS server cannot connect to identd on the client",
    0x5D: "Request rejected: client program and identd report different user-ids",
}


class Socks4Client:
    """SOCKS4/SOCKS4a CONNECT client."""

    @staticmethod
    def connect(
        sock: socket.socket,
        dest_addr: str,
        dest_port: int,
        proxy_type: ProxyType = ProxyType.SOCKS4,
        username: str | None = None,
    ) -> tuple[str, int]:
        """Perform a SOCKS4/4a CONNECT handshake.

        Returns the bound address ``(addr, port)`` from the proxy reply.
        """
        userid = (username or "").encode("ascii")

        if proxy_type == ProxyType.SOCKS4A:
            # SOCKS4a: send invalid IP (0.0.0.x where x != 0) + hostname
            dst_ip = b"\x00\x00\x00\x01"
            hostname = dest_addr.encode("ascii") + b"\x00"
        else:
            # SOCKS4: resolve locally
            try:
                addr_info = socket.getaddrinfo(dest_addr, dest_port, socket.AF_INET)
                host: str = addr_info[0][4][0]  # type: ignore[assignment]
                dst_ip = socket.inet_aton(host)
            except (socket.gaierror, OSError) as exc:
                raise GeneralProxyError(f"Failed to resolve {dest_addr!r}") from exc
            hostname = b""

        # VN(1) CD(1) DSTPORT(2) DSTIP(4) USERID(N) NULL(1) [HOSTNAME]
        request = struct.pack("!BBH", 4, 1, dest_port) + dst_ip + userid + b"\x00" + hostname
        sock.sendall(request)

        # 8-byte response: VN(1) CD(1) DSTPORT(2) DSTIP(4)
        reply = recvall(sock, 8)
        _, cd, bound_port = struct.unpack("!BBH", reply[:4])
        bound_ip = socket.inet_ntoa(reply[4:8])

        if cd != 0x5A:
            error_msg = _SOCKS4_ERRORS.get(cd, f"Unknown SOCKS4 error code: 0x{cd:02X}")
            raise SOCKS4Error(error_msg)

        return bound_ip, bound_port
