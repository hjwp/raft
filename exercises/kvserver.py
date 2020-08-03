from __future__ import annotations
from typing import List, Optional
import socket
import threading
import sys
from dataclasses import dataclass

HOST = '127.0.0.1'

LOG = []   # type: List[SetCommand]




@dataclass
class SetCommand:
    key: str
    val: Optional[str]


def kvget(key: str) -> Optional[str]:
    print('getting', key)
    return next(
        (entry.val for entry in reversed(LOG) if entry.key == key),
        None
    )



def kvset(key: str, val: str) -> None:
    print('setting', key, 'to', val)
    LOG.append(SetCommand(key, val))

def kvdelete(key: str) -> None:
    LOG.append(SetCommand(key, None))


def service_request(req: str):
    cmd, *rest = req.split(',')
    if cmd == "SET":
        key, val = rest
        kvset(key, val)
        return 'OK'
    if cmd == "GET":
        [key] = rest
        result = kvget(key)
        if result is None:
            return f'KEY {key} IS UNSET'
        return f'{key}={result}'
    if cmd == "DELETE":
        [key] = rest
        kvdelete(key)
        return 'OK'
    return f"ERROR CMD={cmd} NOT RECOGNISED"




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
