# pylint: disable=unused-argument, redefined-outer-name
import signal
import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path
from random import randint
from typing import List

import pytest
from transport import connect_tenaciously, HOST, send_message, recv_message


PORTS = [randint(2000, 9999) for _ in range(100)]


@dataclass
class Server:
    process: subprocess.Popen
    port: int

def _start_server(port: int) -> Server:
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
        send_message(s, 'SET,foo,1')
        data = recv_message(s)
        assert data == 'OK'
        send_message(s, 'GET,foo')
        data = recv_message(s)
        assert data == 'foo=1'
        send_message(s, 'SET,foo,3')
        data = recv_message(s)
        assert data == 'OK'
        send_message(s, 'GET,foo')
        data = recv_message(s)
        assert data == 'foo=3'


def test_single_client_get_unknown(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        send_message(s, 'GET,foo')
        data = recv_message(s)
        assert data == 'KEY foo IS UNSET'


def test_single_client_bad_command(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        send_message(s, 'BLARGLE,foo')
        data = recv_message(s)
        assert data == 'ERROR CMD=BLARGLE NOT RECOGNISED'


def test_single_client_delete(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        send_message(s, 'SET,foo,1')
        data = recv_message(s)
        assert data == 'OK'
        send_message(s, 'DELETE,foo')
        data = recv_message(s)
        assert data == 'OK'
        send_message(s, 'GET,foo')
        data = recv_message(s)
        assert data == 'KEY foo IS UNSET'


class KVClient:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        connect_tenaciously(self._sock, self.port, self.host)
        return self

    def __exit__(self, *args):
        self._sock.close()

    def get(self, key: str):
        send_message(self._sock, f'GET,{key}')
        response = recv_message(self._sock)
        if response == f'KEY {key} IS UNSET':
            return None
        nothing, _, val = response.partition(f'{key}=')
        assert nothing == ''
        return val

    def set(self, key: str, val: str) -> None:
        send_message(self._sock, f'SET,{key},{val}')
        response = recv_message(self._sock)
        assert response == 'OK'

    def delete(self, key: str) -> None:
        send_message(self._sock, f'DELETE,{key}')
        response = recv_message(self._sock)
        assert response == 'OK'



def test_kvclient_get_set(server):
    with KVClient(HOST, server.port) as client:
        client.set('bar', 1)
        assert client.get('bar') == '1'
        client.set('bar', 3)
        assert client.get('bar') == '3'

def test_kvclient_two_sets_in_a_row(server):
    with KVClient(HOST, server.port) as client:
        client.set('bar', 1)
        client.set('bar', 2)
        assert client.get('bar') == '2'


def test_kvclient_unknown_and_delete(server):
    with KVClient(HOST, server.port) as client:
        assert client.get('baz') is None
        client.set('baz', 'cabbages')
        assert client.get('baz') == 'cabbages'
        client.delete('baz')
        assert client.get('baz') is None


# pylint: disable=wrong-import-order, wrong-import-position
import random
from concurrent.futures import ThreadPoolExecutor, wait, Future

KEYS = 'foo bar baz cromulent cabbages monkey'.split()

def do_gets_and_sets(job_no, port, done, errors, history):
    with KVClient(HOST, port) as client:
        key = random.choice(KEYS)
        val = str(random.randint(1, 10000))
        client.set(key, val)
        history.append(f'set {key}={val}')
        resp = client.get(key)
        history.append(f'read {key}={val}')
        if resp != val:
            errors.append(f'{key}={resp} did not equal expected: {val}')
        done.append(job_no)


def test_lots_of_kvclients_in_parallel(server):
    pool = ThreadPoolExecutor(max_workers=100)
    done = []  # type: List[str]
    errors = []  # type: List[str]
    jobs = []  # type: List[Future]
    history = []  # type: List[str]
    for i in range(100):
        jobs.append(
            pool.submit(do_gets_and_sets, i, server.port, done, errors, history)
        )
    wait(jobs)
    for job in jobs:
        assert job.exception() is None
    assert len(done) == 100
    for error in errors:
        print('*' * 80)
        key = error.split('=')[0]
        error_read = error.split(' did not equal ')[0]
        error_val = error_read.split('=')[1]
        print(f'*** debuggging {error} ***')
        print('\n'.join(l for l in history if key in l))
        read_pos = history.index(f'read {error_read}')
        write_pos = history.index(f'set {key}={error_val}')
        assert write_pos < read_pos
