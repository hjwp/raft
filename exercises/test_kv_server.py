# pylint: disable=unused-argument, redefined-outer-name
import signal
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from random import randint

import pytest
from echoserver import HOST, send_message, recv_message


PORTS = [randint(2000, 9999) for _ in range(100)]

@dataclass
class Server:
    process: subprocess.Popen
    port: int

def _start_server(port):
    server_path = Path(__file__).parent / 'kvserver.py'
    p = subprocess.Popen(f'python -u {server_path} {port}'.split())
    return Server(process=p, port=port)


@pytest.fixture()
def server():
    server = _start_server(PORTS.pop())
    yield server
    server.process.send_signal(signal.SIGINT)
    server.process.wait()


def connect_tenaciously(s, port):
    tries_left = 10
    while tries_left:
        try:
            print('connection attempt', 11-tries_left)
            s.connect((HOST, port))
            return s
        except ConnectionRefusedError:
            tries_left -= 1
            time.sleep(0.05)


def test_single_client_get_set(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        s.sendall(b'SET,foo,1')
        data = s.recv(1024)
        assert data == b'OK'
        s.sendall(b'GET,foo')
        data = s.recv(1024)
        assert data == b'1'
        s.sendall(b'SET,foo,3')
        data = s.recv(1024)
        assert data == b'OK'
        s.sendall(b'GET,foo')
        data = s.recv(1024)
