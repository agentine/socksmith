"""Tests for SOCKS5/5h protocol client."""

from __future__ import annotations

import socket
import struct
from typing import Any

import pytest

from socksmith._exceptions import GeneralProxyError, SOCKS5AuthError, SOCKS5Error
from socksmith._socks5 import Socks5Client
from socksmith._types import ProxyType


def _success_reply(
    atyp: int = 0x01, addr: bytes = b"\x00\x00\x00\x00", port: int = 0
) -> bytes:
    return (
        struct.pack("!BBB", 0x05, 0x00, 0x00)
        + struct.pack("!B", atyp)
        + addr
        + struct.pack("!H", port)
    )


class TestSocks5NoAuth:
    def test_connect_ipv4(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x00))
        mock_sock.feed(_success_reply())
        bound_addr, bound_port = Socks5Client.connect(
            mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
        )
        assert bound_addr == "0.0.0.0"
        assert bound_port == 0
        assert mock_sock.sent[0] == 0x05
        assert mock_sock.sent[1] == 1
        assert mock_sock.sent[2] == 0x00

    def test_socks5h_domain(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x00))
        mock_sock.feed(_success_reply())
        Socks5Client.connect(
            mock_sock, dest_addr="example.com", dest_port=443, proxy_type=ProxyType.SOCKS5H
        )
        request = bytes(mock_sock.sent[3:])
        assert request[0] == 0x05
        assert request[1] == 0x01
        assert request[3] == 0x03  # domain
        domain_len = request[4]
        assert request[5 : 5 + domain_len] == b"example.com"

    def test_reply_ipv6(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x00))
        ipv6_addr = socket.inet_pton(socket.AF_INET6, "::1")
        mock_sock.feed(_success_reply(atyp=0x04, addr=ipv6_addr, port=1234))
        bound_addr, bound_port = Socks5Client.connect(
            mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
        )
        assert bound_addr == "::1"
        assert bound_port == 1234

    def test_reply_domain(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x00))
        domain = b"proxy.local"
        addr_data = struct.pack("!B", len(domain)) + domain
        mock_sock.feed(_success_reply(atyp=0x03, addr=addr_data, port=9999))
        bound_addr, bound_port = Socks5Client.connect(
            mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
        )
        assert bound_addr == "proxy.local"
        assert bound_port == 9999


class TestSocks5Auth:
    def test_auth_success(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x02))  # select user/pass
        mock_sock.feed(struct.pack("!BB", 0x01, 0x00))  # auth OK
        mock_sock.feed(_success_reply())
        Socks5Client.connect(
            mock_sock,
            dest_addr="93.184.216.34",
            dest_port=80,
            proxy_type=ProxyType.SOCKS5,
            username="user",
            password="pass",
        )
        assert mock_sock.sent[1] == 2  # offered 2 methods
        assert 0x00 in mock_sock.sent[2:4]
        assert 0x02 in mock_sock.sent[2:4]

    def test_auth_failure(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x02))
        mock_sock.feed(struct.pack("!BB", 0x01, 0x01))  # auth rejected
        with pytest.raises(SOCKS5AuthError, match="authentication failed"):
            Socks5Client.connect(
                mock_sock,
                dest_addr="93.184.216.34",
                dest_port=80,
                proxy_type=ProxyType.SOCKS5,
                username="user",
                password="wrong",
            )

    def test_no_acceptable_methods(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0xFF))
        with pytest.raises(SOCKS5AuthError, match="No acceptable"):
            Socks5Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
            )

    def test_auth_required_no_creds(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x02))
        with pytest.raises(SOCKS5AuthError, match="requires username"):
            Socks5Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
            )

    def test_username_too_long(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x02))
        with pytest.raises(SOCKS5AuthError, match="exceeds 255"):
            Socks5Client.connect(
                mock_sock,
                dest_addr="93.184.216.34",
                dest_port=80,
                proxy_type=ProxyType.SOCKS5,
                username="x" * 256,
                password="pass",
            )


class TestSocks5Errors:
    @pytest.mark.parametrize(
        ("code", "msg"),
        [
            (0x01, "General SOCKS server failure"),
            (0x02, "Connection not allowed"),
            (0x03, "Network unreachable"),
            (0x04, "Host unreachable"),
            (0x05, "Connection refused"),
            (0x06, "TTL expired"),
            (0x07, "Command not supported"),
            (0x08, "Address type not supported"),
        ],
    )
    def test_connect_error_codes(self, mock_sock: Any, code: int, msg: str) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x00))
        mock_sock.feed(struct.pack("!BBB", 0x05, code, 0x00))
        with pytest.raises(SOCKS5Error, match=msg):
            Socks5Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
            )

    def test_bad_version_greeting(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x04, 0x00))
        with pytest.raises(GeneralProxyError, match="version"):
            Socks5Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
            )

    def test_bad_version_connect(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x00))
        mock_sock.feed(struct.pack("!BBB", 0x04, 0x00, 0x00))
        with pytest.raises(GeneralProxyError, match="version"):
            Socks5Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
            )

    def test_unsupported_auth_method(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x03))
        with pytest.raises(SOCKS5AuthError, match="Unsupported"):
            Socks5Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
            )

    def test_unsupported_atyp(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x00))
        mock_sock.feed(struct.pack("!BBBB", 0x05, 0x00, 0x00, 0x05))
        with pytest.raises(GeneralProxyError, match="Unsupported address type"):
            Socks5Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
            )

    def test_connection_closed(self, mock_sock: Any) -> None:
        mock_sock.feed(b"\x05")
        with pytest.raises(GeneralProxyError, match="closed"):
            Socks5Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
            )

    def test_unknown_error_code(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BB", 0x05, 0x00))
        mock_sock.feed(struct.pack("!BBB", 0x05, 0x09, 0x00))
        with pytest.raises(SOCKS5Error, match="Unknown"):
            Socks5Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS5
            )
