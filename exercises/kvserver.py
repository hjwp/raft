# pylint: disable=broad-except
from __future__ import annotations
from typing import List, Optional
import socket
import threading
import sys
from dataclasses import dataclass
import sys
from itertools import count
import trio

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


HOST = '127.0.0.1'
CONNECTION_COUNTER = count()

async def kv_server(server_stream):
    ident = next(CONNECTION_COUNTER)
    print(f"kv server {ident}: started")
    try:
        async for data in server_stream:
            print("echo_server {ident}: received data {data!r}")
            result = service_request(data.decode())
            await server_stream.send_all(result.encode())
        print(f"echo_server {ident}: connection closed")
    except Exception as exc:
        print(f"echo_server {ident}: crashed: {exc!r}")

async def main(port: int):
    await trio.serve_tcp(kv_server, port)

if __name__ == '__main__':
    trio.run(main, int(sys.argv[1]))
