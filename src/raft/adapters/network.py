from enum import Enum
from typing import Any, Dict, List, Protocol
from dataclasses import dataclass

from raft.messages import Message


Json = Dict[str, Any]


@dataclass
class Server:
    name: str
    hostname: str
    port: int



class RaftNetwork(Protocol):

    def get_messages(self, to: str) -> List[Message]:
        ...

    def dispatch(self, msg: Message) -> None:
        ...



class RaftTCPNetwork:

    class Servers(Enum):
        S1 = Server('S1', '', 16001)
        S2 = Server('S2', '', 16002)
        S3 = Server('S3', '', 16003)
        S4 = Server('S4', '', 16004)
        S5 = Server('S5', '', 16005)

    def get_messages(self, to: str) -> List[Message]:
        ...

    def dispatch(self, msg: Message) -> None:
        ...
