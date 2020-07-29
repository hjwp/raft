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
    echoserver_path = Path(__file__).parent / 'echoserver.py'
    p = subprocess.Popen(f'python -u {echoserver_path} {port}'.split())
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


def test_wrong_port_returns_connection_refused(server):
    wrong_port = server.port - 1
    assert wrong_port not in PORTS
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            connect_tenaciously(s, server.port)
        except ConnectionRefusedError as e:
            assert e.errno == 111
            assert e.strerror == 'Connection refused'


def test_echo_server_single_client(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        # s.send(b'anything')  # cannot tell if this sends the whole set of bytes.
        send_message(s, b'hello1')  # succeeds with no error even if no-one is doing accept(). returns None
        data1 = recv_message(s)  # blocks
        assert data1 == b'->hello1'
        send_message(s, b'hello2')
        data2 = recv_message(s)
        assert data2 == b'->hello2'


def test_server_cleans_up_ports(server: Server):
    server.process.send_signal(signal.SIGINT)
    server.process.wait()
    try:
        print('starting second server')
        server2 = _start_server(server.port)
        time.sleep(0.2)
        assert server2.process.returncode is None
    finally:
        server.process.kill()



def test_echo_server_multiple_clients_in_series(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        send_message(s, b'hello1')
        data1 = recv_message(s)
        assert data1 == b'->hello1'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        send_message(s, b'hello2')
        data2 = recv_message(s)
        assert data2 == b'->hello2'


def test_echo_server_multiple_clients_in_parallel(server):
    sock = lambda: socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with sock() as s1, sock() as s2:
        connect_tenaciously(s1, server.port)
        connect_tenaciously(s2, server.port)
        send_message(s1, b'hello1')
        data1 = recv_message(s1)
        assert data1 == b'->hello1'
        send_message(s2, b'hello2')
        data2 = recv_message(s2)
        assert data2 == b'->hello2'


def test_echo_server_large_message(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, server.port)
        msg = b' '.join(f'{i:,}'.encode() for i in range(1_000_000))
        # s.send(msg)
        send_message(s, msg)
        data1 = recv_message(s)
        assert data1[:10] == b'->' + msg[:8]
        # print(data1)
        assert len(data1) == len(msg) + 2

import threading
from concurrent.futures import ThreadPoolExecutor, wait

def send_1000_messages(job_no, port, done, errors):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connect_tenaciously(s, port)
        for i in range(1_000):
            msg = f'job {job_no} thread {threading.get_ident()} message {i}'
            send_message(s, msg.encode())
            result = recv_message(s)
            if result != b'->' + msg.encode():
                errors.append(f'Error, {result} != b->{msg}')
            else:
                done.append(msg)



def test_lots_of_messages(server):
    pool = ThreadPoolExecutor(max_workers=100)
    done = []
    errors = []
    jobs = []
    for i in range(1000):
        jobs.append(
            pool.submit(send_1000_messages, i, server.port, done, errors)
        )
    wait(jobs)
    for job in jobs:
        assert job.exception() is None
    assert errors == []
    assert len(done) == 1_000_000

