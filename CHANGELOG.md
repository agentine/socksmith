# Changelog

## 0.1.0 — 2026-03-16

Initial release — modern drop-in replacement for PySocks.

### Added
- SOCKS4 and SOCKS4a proxy client with local/remote DNS resolution
- SOCKS5 and SOCKS5h proxy client with no-auth and username/password authentication (RFC 1929)
- HTTP CONNECT proxy client with Basic auth support
- `socksocket` class (subclass of `socket.socket`) for transparent proxy tunneling
- `set_default_proxy()` / `get_default_proxy()` for thread-safe global proxy configuration
- `create_connection()` proxy-aware connection factory
- `socks.py` compatibility shim with PySocks constants (`PROXY_TYPE_SOCKS4`, `PROXY_TYPE_SOCKS5`, `PROXY_TYPE_HTTP`)
- Full PySocks-compatible exception hierarchy
- Complete type annotations with `py.typed` marker
- Zero dependencies, Python 3.10+
