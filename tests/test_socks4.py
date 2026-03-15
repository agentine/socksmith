"""Tests for SOCKS4/4a protocol client."""

from __future__ import annotations

import socket
import struct
from typing import Any

import pytest

from socksmith._exceptions import GeneralProxyError, SOCKS4Error
from socksmith._socks4 import Socks4Client
from socksmith._types import ProxyType


class TestSocks4Connect:
    def test_success(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BBH4s", 0, 0x5A, 0, b"\x00\x00\x00\x00"))
        bound_addr, bound_port = Socks4Client.connect(
            mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS4
        )
        assert bound_addr == "0.0.0.0"
        assert bound_port == 0
        sent = mock_sock.sent
        assert sent[0] == 4  # VN
        assert sent[1] == 1  # CD
        assert struct.unpack("!H", sent[2:4])[0] == 80
        assert sent[4:8] == socket.inet_aton("93.184.216.34")
        assert sent[8] == 0  # null-terminated empty userid

    def test_with_username(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BBH4s", 0, 0x5A, 0, b"\x00\x00\x00\x00"))
        Socks4Client.connect(
            mock_sock,
            dest_addr="93.184.216.34",
            dest_port=80,
            proxy_type=ProxyType.SOCKS4,
            username="testuser",
        )
        sent = mock_sock.sent
        null_pos = sent.index(0, 8)
        assert sent[8:null_pos] == b"testuser"

    def test_socks4a_remote_dns(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BBH4s", 0, 0x5A, 0, b"\x00\x00\x00\x00"))
        Socks4Client.connect(
            mock_sock, dest_addr="example.com", dest_port=443, proxy_type=ProxyType.SOCKS4A
        )
        sent = mock_sock.sent
        assert sent[4:8] == b"\x00\x00\x00\x01"  # invalid IP triggers 4a
        assert b"example.com\x00" in sent

    def test_rejected(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BBH4s", 0, 0x5B, 0, b"\x00\x00\x00\x00"))
        with pytest.raises(SOCKS4Error, match="rejected"):
            Socks4Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS4
            )

    def test_identd_error(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BBH4s", 0, 0x5C, 0, b"\x00\x00\x00\x00"))
        with pytest.raises(SOCKS4Error, match="identd"):
            Socks4Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS4
            )

    def test_userid_mismatch(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BBH4s", 0, 0x5D, 0, b"\x00\x00\x00\x00"))
        with pytest.raises(SOCKS4Error, match="user-id"):
            Socks4Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS4
            )

    def test_unknown_error_code(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BBH4s", 0, 0xFF, 0, b"\x00\x00\x00\x00"))
        with pytest.raises(SOCKS4Error, match="Unknown"):
            Socks4Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS4
            )

    def test_connection_closed(self, mock_sock: Any) -> None:
        mock_sock.feed(b"\x00\x5A")  # only 2 bytes instead of 8
        with pytest.raises(GeneralProxyError, match="closed"):
            Socks4Client.connect(
                mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS4
            )

    def test_bound_address(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BBH", 0, 0x5A, 8080) + socket.inet_aton("10.0.0.1"))
        bound_addr, bound_port = Socks4Client.connect(
            mock_sock, dest_addr="93.184.216.34", dest_port=80, proxy_type=ProxyType.SOCKS4
        )
        assert bound_addr == "10.0.0.1"
        assert bound_port == 8080

    def test_high_port(self, mock_sock: Any) -> None:
        mock_sock.feed(struct.pack("!BBH4s", 0, 0x5A, 0, b"\x00\x00\x00\x00"))
        Socks4Client.connect(
            mock_sock, dest_addr="example.com", dest_port=65535, proxy_type=ProxyType.SOCKS4A
        )
        assert struct.unpack("!H", mock_sock.sent[2:4])[0] == 65535
