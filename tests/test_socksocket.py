"""Tests for socksocket class and create_connection."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from socksmith._exceptions import GeneralProxyError
from socksmith._globals import get_default_proxy, set_default_proxy
from socksmith._socket import socksocket
from socksmith._types import ProxyType


class TestSocksSocket:
    def test_set_proxy(self) -> None:
        sock = socksocket()
        sock.set_proxy(ProxyType.SOCKS5, "proxy.local", 1080)
        assert sock._proxy[0] == ProxyType.SOCKS5
        assert sock._proxy[1] == "proxy.local"
        assert sock._proxy[2] == 1080
        sock.close()

    def test_setproxy_alias(self) -> None:
        sock = socksocket()
        # setproxy is a class-level alias; bound methods won't be `is`-identical
        assert socksocket.setproxy is socksocket.set_proxy
        sock.close()

    def test_default_proxy_fallback(self) -> None:
        set_default_proxy(ProxyType.HTTP, "default.proxy", 8080)
        try:
            sock = socksocket()
            proxy = sock._get_proxy()
            assert proxy[0] == ProxyType.HTTP
            assert proxy[1] == "default.proxy"
            assert proxy[2] == 8080
            sock.close()
        finally:
            set_default_proxy()

    def test_instance_proxy_overrides_default(self) -> None:
        set_default_proxy(ProxyType.HTTP, "default.proxy", 8080)
        try:
            sock = socksocket()
            sock.set_proxy(ProxyType.SOCKS5, "instance.proxy", 1080)
            proxy = sock._get_proxy()
            assert proxy[0] == ProxyType.SOCKS5
            assert proxy[1] == "instance.proxy"
            sock.close()
        finally:
            set_default_proxy()

    @patch.object(socksocket, "connect", autospec=False)
    def test_connect_ex_success(self, mock_connect: MagicMock) -> None:
        mock_connect.return_value = None
        sock = socksocket()
        result = sock.connect_ex(("example.com", 80))
        assert result == 0
        sock.close()

    @patch.object(socksocket, "connect", autospec=False)
    def test_connect_ex_failure(self, mock_connect: MagicMock) -> None:
        err = OSError("fail")
        err.errno = 111
        mock_connect.side_effect = err
        sock = socksocket()
        result = sock.connect_ex(("example.com", 80))
        assert result == 111
        sock.close()

    def test_no_proxy_addr_raises(self) -> None:
        sock = socksocket()
        sock.set_proxy(ProxyType.SOCKS5)
        with pytest.raises(GeneralProxyError, match="address not set"):
            sock.connect(("example.com", 80))
        sock.close()


class TestDefaultProxy:
    def test_initial_none(self) -> None:
        set_default_proxy()
        proxy = get_default_proxy()
        assert proxy[0] is None

    def test_set_and_get(self) -> None:
        set_default_proxy(ProxyType.SOCKS5, "proxy.local", 1080, True, "user", "pass")
        try:
            proxy = get_default_proxy()
            assert proxy == (ProxyType.SOCKS5, "proxy.local", 1080, True, "user", "pass")
        finally:
            set_default_proxy()

    def test_reset(self) -> None:
        set_default_proxy(ProxyType.HTTP, "proxy", 8080)
        set_default_proxy()
        assert get_default_proxy()[0] is None
