# socksmith — Drop-in Python Replacement for PySocks

## Target
**PySocks** (`pip install PySocks`) — SOCKS proxy client library.
- **Repo:** github.com/Anorov/PySocks
- **Last release:** v1.7.1 (Sep 2019) — abandoned 6+ years
- **Downloads:** ~56M/month on PyPI
- **Dependents:** ~241,000 packages (key consumer: `urllib3[socks]` / `requests[socks]`)
- **License:** BSD
- **Issues:** 50 open issues, 14 open PRs, zero maintainer engagement since 2019

## Why Replace
- Single maintainer (Anorov) completely inactive since 2019
- No Python 3.10+ testing or type hints
- No async/await support
- Known bugs unpatched (timeout handling, SOCKS5 auth edge cases)
- `python-socks` exists but is **not** API-compatible — a drop-in replacement is needed

## Package Name
**socksmith** (verified available on PyPI)

## Scope
Drop-in replacement for PySocks with the same public API surface, plus modern improvements.

## Architecture

### Core Module: `socksmith`
- `socksocket` class — subclass of `socket.socket` with proxy tunneling
- `set_default_proxy()` / `get_default_proxy()` — global proxy configuration
- `create_connection()` — proxy-aware connection factory
- Monkey-patching support via `socksocket` as drop-in for `socket.socket`

### Protocol Support
- **SOCKS4** — basic SOCKS4 connect
- **SOCKS4a** — SOCKS4 with remote DNS resolution
- **SOCKS5** — full SOCKS5 with optional auth (username/password)
- **SOCKS5h** — SOCKS5 with remote DNS (hostname-based)
- **HTTP CONNECT** — HTTP proxy tunneling

### Compatibility Layer
- `socks` module alias for PySocks drop-in compatibility
- Same constants: `PROXY_TYPE_SOCKS4`, `PROXY_TYPE_SOCKS5`, `PROXY_TYPE_HTTP`
- Same exception classes: `ProxyError`, `GeneralProxyError`, `ProxyConnectionError`, `SOCKS5AuthError`, `SOCKS5Error`, `SOCKS4Error`, `HTTPError`

## Major Components

1. **SOCKS4/4a Client** — connect request, response parsing, error handling
2. **SOCKS5 Client** — greeting, auth negotiation (none, username/password), connect, bind, UDP associate
3. **HTTP CONNECT Client** — CONNECT method tunneling with basic/digest auth
4. **Socket Wrapper** — `socksocket` class wrapping `socket.socket`
5. **DNS Resolution** — local vs remote DNS resolution based on proxy type
6. **Timeout Handling** — proper timeout propagation through proxy handshake

## Improvements Over PySocks
- Python 3.10+ only (drop Python 2 / old 3.x baggage)
- Full type annotations (py.typed marker)
- Async support via `asyncio` (`AsyncSocksSocket`)
- Proper timeout handling during proxy negotiation
- Better error messages with proxy details
- Zero dependencies
- 100% test coverage target

## Deliverables
- `socksmith/` package with full PySocks-compatible API
- `pyproject.toml` with modern build config
- Comprehensive test suite (unit + integration with local SOCKS server)
- README with migration guide from PySocks
- `socks` compatibility alias module

## Non-Goals
- UDP relay (document as future work)
- SOCKS5 BIND command (rarely used)
- urllib2 handler (Python 2 era, use urllib3 instead)
