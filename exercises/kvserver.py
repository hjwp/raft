from __future__ import annotations
from typing import List, Optional
import socket
import threading
import traceback
import sys
from dataclasses import dataclass
from colorama import Style, Fore

from transport import HOST, send_message, recv_message, ConnectionClosed

def _tid() -> str:
    tid = threading.get_ident()
    return f'Thread-{tid}'

def _kvdebug(msg) -> None:
    print(f'{Style.DIM}[kvstore][{_tid()}] {msg}{Style.RESET_ALL}')

def _serverdebug(msg) -> None:
    print(f'{Fore.YELLOW}[server][{_tid()}] {msg}{Style.RESET_ALL}')

def _msgdebug(msg) -> None:
    print(f'{Style.DIM}[server][{_tid()}] {msg}{Style.RESET_ALL}')

def _errordebug(msg) -> None:
    print(f'{Fore.RED}[error][{_tid()}] {msg}{Style.RESET_ALL}')

LOG = []   # type: List[SetCommand]



@dataclass
class SetCommand:
    key: str
    val: Optional[str]


def kvget(key: str) -> Optional[str]:
    _kvdebug(f'getting {key}')
    return next(
        (entry.val for entry in reversed(LOG) if entry.key == key),
        None
    )



def kvset(key: str, val: str) -> None:
    _kvdebug(f'setting {key} to {val}')
    LOG.append(SetCommand(key, val))

def kvdelete(key: str) -> None:
    _kvdebug(f'deleting {key}')
    LOG.append(SetCommand(key, None))


def service_request(req: str) -> str:
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




def handle_kv_requests(conn: socket.socket, remote_port: int) -> None:
    with conn:
        _serverdebug(f'starting kv handler for connection {remote_port}')
        while True:
            try:
                try:
                    data = recv_message(conn)
                except ConnectionClosed:
                    _serverdebug(f'ending server for connection {remote_port}')
                    return
                _serverdebug(f'received message {data!r}')
                result = service_request(data)
                send_message(conn, result)
            except Exception:
                _errordebug(traceback.format_exc())
                return



def main(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        _serverdebug(f'binding to {port}')
        s.bind((HOST, port))  # may return OSError 98, address already in use
        _serverdebug(f'listening on {port}')
        s.listen()
        _serverdebug(f"waiting to accept connection on {port}")
        threads = []
        while True:
            conn, (_, remote_port) = s.accept()  # this hangs until someone connects
            _serverdebug(f'got connection to {port} from port {remote_port}')
            thread = threading.Thread(
                target=handle_kv_requests,
                args=(conn, remote_port)
            )
            threads.append(thread)
            thread.start()

if __name__ == '__main__':
    main(int(sys.argv[1]))
