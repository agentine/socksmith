# socksmith

Modern drop-in replacement for [PySocks](https://github.com/Anorov/PySocks) — SOCKS and HTTP proxy client for Python 3.10+.

## Installation

```bash
pip install socksmith
```

## Quick Start

```python
import socksmith

# Create a SOCKS5 proxied socket
sock = socksmith.socksocket()
sock.set_proxy(socksmith.SOCKS5, "proxy.example.com", 1080)
sock.connect(("example.com", 80))

# Or use the module-level default
socksmith.set_default_proxy(socksmith.SOCKS5, "proxy.example.com", 1080)
sock = socksmith.socksocket()
sock.connect(("example.com", 80))
```

## Migration from PySocks

socksmith is a drop-in replacement. Change your import:

```python
# Before
import socks

# After — still works!
import socks  # socksmith provides this compatibility module
```

All PySocks constants, exceptions, and classes are available:

```python
import socks

socks.PROXY_TYPE_SOCKS4  # = 1
socks.PROXY_TYPE_SOCKS5  # = 2
socks.PROXY_TYPE_HTTP    # = 3
```

## Features

- **Drop-in PySocks replacement** — same API, same constants, same exceptions
- **SOCKS4/4a** — with remote DNS resolution
- **SOCKS5/5h** — with username/password auth (RFC 1929)
- **HTTP CONNECT** — with Basic authentication
- **Python 3.10+** — no legacy baggage
- **Fully typed** — PEP 561 compliant (`py.typed`)
- **Zero dependencies**

## License

BSD-3-Clause
