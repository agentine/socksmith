"""Tests for HTTP CONNECT proxy client."""

from __future__ import annotations

import base64
from typing import Any

import pytest

from socksmith._exceptions import GeneralProxyError, HTTPError
from socksmith._http import HttpConnectClient


class TestHttpConnect:
    def test_success(self, mock_sock: Any) -> None:
        mock_sock.feed(b"HTTP/1.1 200 Connection established\r\n\r\n")
        addr, port = HttpConnectClient.connect(mock_sock, dest_addr="example.com", dest_port=443)
        assert addr == "example.com"
        assert port == 443
        sent = mock_sock.sent.decode("ascii")
        assert "CONNECT example.com:443 HTTP/1.1" in sent
        assert "Host: example.com:443" in sent

    def test_with_auth(self, mock_sock: Any) -> None:
        mock_sock.feed(b"HTTP/1.1 200 OK\r\n\r\n")
        HttpConnectClient.connect(
            mock_sock, dest_addr="example.com", dest_port=443, username="user", password="pass"
        )
        sent = mock_sock.sent.decode("ascii")
        expected_creds = base64.b64encode(b"user:pass").decode("ascii")
        assert f"Proxy-Authorization: Basic {expected_creds}" in sent

    def test_no_auth_header_without_creds(self, mock_sock: Any) -> None:
        mock_sock.feed(b"HTTP/1.1 200 OK\r\n\r\n")
        HttpConnectClient.connect(mock_sock, dest_addr="example.com", dest_port=443)
        sent = mock_sock.sent.decode("ascii")
        assert "Proxy-Authorization" not in sent

    def test_407_error(self, mock_sock: Any) -> None:
        mock_sock.feed(b"HTTP/1.1 407 Proxy Authentication Required\r\n\r\n")
        with pytest.raises(HTTPError, match="407"):
            HttpConnectClient.connect(mock_sock, dest_addr="example.com", dest_port=443)

    def test_403_error(self, mock_sock: Any) -> None:
        mock_sock.feed(b"HTTP/1.1 403 Forbidden\r\n\r\n")
        with pytest.raises(HTTPError, match="403"):
            HttpConnectClient.connect(mock_sock, dest_addr="example.com", dest_port=443)

    def test_503_error(self, mock_sock: Any) -> None:
        mock_sock.feed(b"HTTP/1.1 503 Service Unavailable\r\n\r\n")
        with pytest.raises(HTTPError, match="503"):
            HttpConnectClient.connect(mock_sock, dest_addr="example.com", dest_port=443)

    def test_connection_closed(self, mock_sock: Any) -> None:
        mock_sock.feed(b"HTTP/1.1 200")
        with pytest.raises(GeneralProxyError, match="closed"):
            HttpConnectClient.connect(mock_sock, dest_addr="example.com", dest_port=443)

    def test_malformed_response(self, mock_sock: Any) -> None:
        mock_sock.feed(b"GARBAGE\r\n\r\n")
        with pytest.raises(GeneralProxyError, match="Malformed HTTP response"):
            HttpConnectClient.connect(mock_sock, dest_addr="example.com", dest_port=443)

    def test_extra_headers(self, mock_sock: Any) -> None:
        mock_sock.feed(b"HTTP/1.1 200 OK\r\nX-Proxy: test\r\n\r\n")
        addr, port = HttpConnectClient.connect(
            mock_sock, dest_addr="example.com", dest_port=8443
        )
        assert addr == "example.com"
        assert port == 8443

    def test_high_port(self, mock_sock: Any) -> None:
        mock_sock.feed(b"HTTP/1.1 200 OK\r\n\r\n")
        HttpConnectClient.connect(mock_sock, dest_addr="example.com", dest_port=65535)
        sent = mock_sock.sent.decode("ascii")
        assert "CONNECT example.com:65535" in sent
