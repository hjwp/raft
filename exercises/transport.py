import time
from socket import socket
from colorama import Style

class ConnectionClosed(ConnectionError):
    pass


def _log(msg):
    print(f'{Style.DIM}[transport] {msg}{Style.RESET_ALL}')

HOST = '127.0.0.1'

def send_message(sock: socket, msg: str) -> None:
    size_prefix = b'%12d' % len(msg)
    sock.sendall(size_prefix + msg.encode())


def _recv_exactly(sock: socket, num_bytes: int) -> str:
    # Receive exactly a requested number of bytes on a socket
    msg = b''
    while num_bytes:
        part = sock.recv(num_bytes)  # No guarantee we get the complete message
        if part == b'':
            raise EOFError(f'Client disconnected with partial message {msg!r}')
        msg += part
        num_bytes -= len(part)
    return msg.decode()

def recv_message(sock: socket) -> str:
    try:
        expected_size = int(_recv_exactly(sock, 12))
    except EOFError:
        raise ConnectionClosed('Client disconnected')
    return _recv_exactly(sock, expected_size)


def connect_tenaciously(s: socket, port: int, host: str = HOST) -> socket:
    tries_left = 10
    while True:
        try:
            print('connection attempt', 11-tries_left)
            s.connect((host, port))
            return s
        except ConnectionRefusedError:
            tries_left -= 1
            if tries_left == 0:
                raise
            time.sleep(0.05)
