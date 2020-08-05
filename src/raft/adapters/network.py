from enum import Enum
from typing import Any, Dict, List, Protocol
from dataclasses import dataclass
import pickle
import queue
import socket
import threading

from raft.messages import Message
from . import transport


class RaftNetwork(Protocol):

    def get_messages(self, to: str) -> List[Message]:
        ...

    def dispatch(self, msg: Message) -> None:
        ...


# -- Dave's code, modified

def receive_message(sock: socket.socket) -> Message:
    raw = transport.recv_message(sock)
    result = pickle.loads(raw)
    assert isinstance(result, Message)
    return result

def send_message(msg: Message, sock: socket.socket) -> None:
    transport.send_message(sock, pickle.dumps(msg))


@dataclass
class Host:
    name: str
    hostname: str
    port: int


class TCPRaftNet:
    SERVERS = {
        'S1': ('localhost', 16001),
        'S2': ('localhost', 16002),
        'S3': ('localhost', 16003),
        'S4': ('localhost', 16004),
        'S5': ('localhost', 16005),
    }

    def __init__(self, name) -> None:
        self.host = self.SERVERS[name]
        # Message queues.  There is a separate outgoing queue for each destination.
        # There is a single incoming queue for all received messages.
        self._outgoing = {name: queue.Queue() for name in self.SERVERS}  # type: Dict[str, queue.Queue]
        self._incoming = queue.Queue()  # type: queue.Queue[Message]

    def dispatch(self, msg: Message) -> None:
        # Drop the message in a queue and walk away immediately. Does NOT block.
        self._outgoing[msg.to].put(msg)


    def get_messages(self) -> List[Message]:
        messages = []
        while not self._incoming.empty():
            messages.append(self._incoming.get())
        return messages


    def start(self):
        # Launch various threads related to the network component

        # Thread responsible for listening for incoming connections
        threading.Thread(target=self.acceptor_thread, daemon=True).start()

        # Threads dedicated to sending outgoing messages
        for server_name in self._outgoing:
            threading.Thread(target=self.sender_thread, args=(server_name,), daemon=True).start()

    def acceptor_thread(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.bind(self.host)
        sock.listen()
        while True:
            client, addr = sock.accept()
            threading.Thread(target=self.receiver_thread, args=(client,), daemon=True).start()

    def receiver_thread(self, sock):
        # Thread that deals with messages
        try:
            while True:
                msg = receive_message(sock)
                self._incoming.put(msg)
        except (EOFError, ConnectionError):
            sock.close()

    def sender_thread(self, server_name):
        sock = None
        while True:
            msg = self._outgoing[server_name].get()
            # Make some kind of best-effort to send the message
            if sock is None:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect(self.SERVERS[server_name])
                except OSError:
                    sock.close()
                    sock = None
                    continue       # Oh well. Throw the message away.

            try:
                send_message(msg, sock)
            except OSError:
                sock.close()
                sock = None
