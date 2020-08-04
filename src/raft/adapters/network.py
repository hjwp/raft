from enum import Enum
from typing import Protocol, Dict
from dataclasses import dataclass

Json = Dict[str, ...]


@dataclass
class Server:
    name: str
    hostname: str
    port: int



class RaftNetwork(Protocol):

    def send_message(self, to: str, msg: Json):
        ...

    def recv_message(self, to: str, msg: Json):
        ...


class RaftTCPNetwork:
    class Servers(Enum):
        S1 = Server('S1', '', 16001)
        S2 = Server('S2', '', 16002)
        S3 = Server('S3', '', 16003)
        S4 = Server('S4', '', 16004)
        S5 = Server('S5', '', 16005)

    def send_message(self, to: str, msg: Json):
        [server] = [s for s in self.Servers if s.name == to]
        ...
