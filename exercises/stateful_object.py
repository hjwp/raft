# pylint: disable=no-self-use,redefined-builtin
from __future__ import annotations
from typing import Protocol
from socket import socket, AF_INET, SOCK_STREAM

class ConnectionError(Exception):
    pass


class Socket(Protocol):

    def connect(self, host: str, port: int) -> OpenSocket:
        ...

    def send(self, msg: bytes) -> int:
        ...

    def recv(self, maxbytes: int) -> bytes:
        ...

    def close(self) -> ClosedSocket:
        ...


class ClosedSocket:

    def connect(self, host, port):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host, port))
        return OpenSocket(sock)

    def send(self, msg):
        raise ConnectionError("Not open")

    def recv(self, maxbytes):
        raise ConnectionError("Not open")

    def close(self):
        raise ConnectionError("Not open")


class OpenSocket:

    def __init__(self, sock: socket):
        self._sock = sock

    def connect(self, host, port):
        raise ConnectionError("Not closed")

    def send(self, msg):
        return self._sock.send(msg)

    def recv(self, maxbytes):
        return self._sock.recv(maxbytes)

    def close(self):
        self._sock.close()
        return ClosedSocket()


class Connection:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = ClosedSocket()

    def connect(self):
        self.sock = self.sock.connect(self.host, self.port)

    def send(self, msg):
        return self.sock.send(msg)

    def recv(self, maxbytes):
        return self.sock.recv(maxbytes)

    def close(self):
        self.sock = self.sock.close()
