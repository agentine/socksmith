"""Shared test fixtures."""

from __future__ import annotations

import pytest


class MockSocket:
    """A mock socket that records sent data and replays responses."""

    def __init__(self) -> None:
        self.sent = bytearray()
        self._recv_buffer = bytearray()

    def feed(self, data: bytes) -> None:
        """Queue data to be returned by recv()."""
        self._recv_buffer.extend(data)

    def sendall(self, data: bytes) -> None:
        self.sent.extend(data)

    def recv(self, bufsize: int) -> bytes:
        if not self._recv_buffer:
            return b""
        chunk = bytes(self._recv_buffer[:bufsize])
        del self._recv_buffer[:bufsize]
        return chunk

    def settimeout(self, timeout: float | None) -> None:
        pass

    def close(self) -> None:
        pass


@pytest.fixture
def mock_sock() -> MockSocket:
    """Return a fresh MockSocket."""
    return MockSocket()
