from typing import List
import socket
import threading
import time
import sys
from dataclasses import dataclass

HOST = '127.0.0.1'

LOG = []   # type: List[SetCommand]



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


class KVClient:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__():
        pass



@dataclass
class SetCommand:
    key: str
    val: str


def kvget(key):
    print('getting', key)
    return next(
        entry.val
        for entry in reversed(LOG)
        if entry.key == key
    )

def kvset(key, val):
    print('setting', key, 'to', val)
    LOG.append(SetCommand(key, val))


def service_request(req):
    cmd, *rest = req.split(',')
    if cmd == "SET":
        key, val = rest
        kvset(key, val)
        return 'OK'
    if cmd == "GET":
        [key] = rest
        return kvget(key)
    # TODO: use Json to be able to return out-of-band stuff, eg errors.
    return None




def handle_kv_requests(conn, remote_port):
    with conn:
        print('starting kv handler for connection', remote_port)
        while True:
            data = conn.recv(1024)
            if not data:
                print('ending server for connection', remote_port)
                return
            print(f'received message {data}')
            result = service_request(data.decode())
            conn.sendall(result.encode())

def main(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # need to call both bind() and listen(), otherwise
        # client will see `ConnectionRefusedError`
        # print('binding to', port, '\n\t', s)
        print('binding to', port)
        s.bind((HOST, port))  # may return OSError 98, address already in use
        print('listening on', port)
        s.listen()
        print("waiting to accept connection on", port)
        threads = []
        while True:
            conn, (_, remote_port) = s.accept()  # this hangs until someone connects
            print('got connection to', port, 'from port', remote_port)
            thread = threading.Thread(
                target=handle_kv_requests,
                args=(conn, remote_port)
            )
            threads.append(thread)
            thread.start()

if __name__ == '__main__':
    main(int(sys.argv[1]))
