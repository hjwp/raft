# pylint: disable=unused-argument, redefined-outer-name
import signal
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from random import randint
from typing import Optional

import pytest
from kvserver import HOST


def connect_tenaciously(s, port, host=HOST):
    tries_left = 10
    while tries_left:
        try:
            print('connection attempt', 11-tries_left)
            s.connect((HOST, port))
            return s
        except ConnectionRefusedError:
            tries_left -= 1
            time.sleep(0.05)

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


def test_single_client_get_set(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        s.sendall(b'SET,foo,1')
        data = s.recv(1024)
        assert data == b'OK'
        s.sendall(b'GET,foo')
        data = s.recv(1024)
        assert data == b'foo=1'
        s.sendall(b'SET,foo,3')
        data = s.recv(1024)
        assert data == b'OK'
        s.sendall(b'GET,foo')
        data = s.recv(1024)
        assert data == b'foo=3'


def test_single_client_get_unknown(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        s.sendall(b'GET,foo')
        data = s.recv(1024)
        assert data == b'KEY foo IS UNSET'


def test_single_client_bad_command(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        s.sendall(b'BLARGLE,foo')
        data = s.recv(1024)
        assert data == b'ERROR CMD=BLARGLE NOT RECOGNISED'


def test_single_client_delete(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        s.sendall(b'SET,foo,1')
        data = s.recv(1024)
        assert data == b'OK'
        s.sendall(b'DELETE,foo')
        data = s.recv(1024)
        assert data == b'OK'
        s.sendall(b'GET,foo')
        data = s.recv(1024)
        assert data == b'KEY foo IS UNSET'


class KVClient:

    def __init__(self, host:str, port:int):
        self.host = host
        self.port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        connect_tenaciously(self._sock, self.port, self.host)
        return self

    def __exit__(self, *args):
        self._sock.close()

    def get(self, key:str):
        self._sock.sendall(f'GET,{key}'.encode())
        response = self._sock.recv(1024).decode()
        if response == f'KEY {key} IS UNSET':
            return None
        nothing, _, val = response.partition(f'{key}=')
        assert nothing == ''
        return val

    def set(self, key:str, val:str) -> None:
        self._sock.sendall(f'SET,{key},{val}'.encode())
        response = self._sock.recv(1024)
        assert response == b'OK'

    def delete(self, key:str) -> None:
        self._sock.sendall(f'DELETE,{key}'.encode())
        response = self._sock.recv(1024)
        assert response == b'OK'



def test_kvclient_get_set(server):
    with KVClient(HOST, server.port) as client:
        client.set('bar', 1)
        assert client.get('bar') == '1'
        client.set('bar', 3)
        assert client.get('bar') == '3'


def test_kvclient_unknown_and_delete(server):
    with KVClient(HOST, server.port) as client:
        assert client.get('baz') is None
        client.set('baz', 'cabbages')
        assert client.get('baz') == 'cabbages'
        client.delete('baz')
        assert client.get('baz') is None


import random
import threading
from concurrent.futures import ThreadPoolExecutor, wait

def do_gets_and_sets(job_no, port, done, errors):
    with KVClient(HOST, port) as client:
        key = random.choice('foo bar baz cromulent cabbages monkey')
        val = str(random.randint(1, 10000))
        client.set(key, val)
        # TODO

def test_lots_of_kvclients_in_parallel(server):
    pool = ThreadPoolExecutor(max_workers=100)
    done = []
    errors = []
    jobs = []
    for i in range(100):
        jobs.append(
            pool.submit(do_gets_and_sets, i, server.port, done, errors)
        )
    wait(jobs)
    for job in jobs:
        assert job.exception() is None
    assert errors == []
    assert len(done) == 1_000_000


