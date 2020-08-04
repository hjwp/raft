from typing import Dict, List
from collections import defaultdict
from raft.adapters.run_server import clock_tick
from raft.log import InMemoryLog
from raft.messages import Message, ClientSetCommand
from raft.server import Leader, Follower

class FakeRaftNetwork:
    def __init__(self, me: str, peers: List[str]):
        self.me = me
        self.peers = peers
        self.messages = []  # type: List[Message]

    def get_messages(self) -> List[Message]:
        return [m for m in self.messages if m.to == self.me]

    def dispatch(self, msg: Message) -> None:
        self.messages.append(msg)


def test_replication():
    peers = ("S2",)

    leader_log = InMemoryLog([])
    leader = Leader(
        name="S1", peers=peers, log=leader_log, currentTerm=1, votedFor=None
    )

    follower_log = InMemoryLog([])
    follower = Follower(name="S2", log=follower_log, currentTerm=1, votedFor=None)

    leader.handle_message(Message(frm='client.id', to='S1', cmd=ClientSetCommand(
        'foo=1'
    )))

