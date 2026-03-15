"""Tests for PySocks compatibility layer."""

from __future__ import annotations


class TestCompatImports:
    def test_import_socks(self) -> None:
        import socks

        assert socks is not None

    def test_proxy_type_constants(self) -> None:
        import socks

        assert hasattr(socks, "PROXY_TYPE_SOCKS4")
        assert hasattr(socks, "PROXY_TYPE_SOCKS5")
        assert hasattr(socks, "PROXY_TYPE_HTTP")

    def test_short_aliases(self) -> None:
        import socks

        assert hasattr(socks, "SOCKS4")
        assert hasattr(socks, "SOCKS5")
        assert hasattr(socks, "HTTP")

    def test_extended_types(self) -> None:
        import socks

        assert hasattr(socks, "SOCKS4A")
        assert hasattr(socks, "SOCKS5H")
        assert hasattr(socks, "PROXY_TYPE_SOCKS4A")
        assert hasattr(socks, "PROXY_TYPE_SOCKS5H")

    def test_exception_classes(self) -> None:
        import socks

        assert issubclass(socks.ProxyError, OSError)
        assert issubclass(socks.GeneralProxyError, socks.ProxyError)
        assert issubclass(socks.ProxyConnectionError, socks.ProxyError)
        assert issubclass(socks.SOCKS5AuthError, socks.ProxyError)
        assert issubclass(socks.SOCKS5Error, socks.ProxyError)
        assert issubclass(socks.SOCKS4Error, socks.ProxyError)
        assert issubclass(socks.HTTPError, socks.ProxyError)

    def test_socksocket_class(self) -> None:
        import socks

        assert hasattr(socks, "socksocket")

    def test_functions(self) -> None:
        import socks

        assert callable(socks.set_default_proxy)
        assert callable(socks.get_default_proxy)
        assert callable(socks.create_connection)
        assert callable(socks.setdefaultproxy)

    def test_proxy_types_dict(self) -> None:
        import socks

        assert isinstance(socks.PROXY_TYPES, dict)
        assert socks.PROXY_TYPES[socks.SOCKS5] == "SOCKS5"

    def test_default_ports_dict(self) -> None:
        import socks

        assert isinstance(socks.DEFAULT_PORTS, dict)
        assert socks.DEFAULT_PORTS[socks.SOCKS5] == 1080
        assert socks.DEFAULT_PORTS[socks.HTTP] == 8080

    def test_constant_values_are_ints(self) -> None:
        import socks

        assert isinstance(int(socks.PROXY_TYPE_SOCKS4), int)
        assert isinstance(int(socks.PROXY_TYPE_SOCKS5), int)
        assert isinstance(int(socks.PROXY_TYPE_HTTP), int)

    def test_pysocks_compat_values(self) -> None:
        """PySocks used SOCKS4=1, SOCKS5=2, HTTP=3."""
        import socks

        assert int(socks.PROXY_TYPE_SOCKS4) == 1
        assert int(socks.PROXY_TYPE_SOCKS5) == 2
        assert int(socks.PROXY_TYPE_HTTP) == 3
