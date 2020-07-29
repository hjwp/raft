from unittest import mock
import pytest
from stateful_object import Connection, ConnectionError

@pytest.fixture(autouse=True)
def fake_socket():
    with mock.patch('stateful_object.socket'):
        yield

def test_cannot_connect_if_not_closed():
    conn = Connection('host', 'port')
    conn.connect()
    with pytest.raises(ConnectionError):
        conn.connect()

def test_cannot_send_if_not_open():
    conn = Connection('host', 'port')
    with pytest.raises(ConnectionError):
        conn.send('foo')

def test_cannot_recv_if_not_open():
    conn = Connection('host', 'port')
    with pytest.raises(ConnectionError):
        conn.recv(10)

def test_cannot_recv_if_not_open():
    conn = Connection('host', 'port')
    with pytest.raises(ConnectionError):
        conn.recv(10)

def test_cannot_close_if_not_open():
    conn = Connection('host', 'port')
    with pytest.raises(ConnectionError):
        conn.close()
