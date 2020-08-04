from typing import List
from raft.adapters.run_server import clock_tick
from raft.log import InMemoryLog
from raft.messages import Message, ClientSetCommand
from raft.server import Leader, Follower


class FakeRaftNetwork:
    def __init__(self, messages: List[Message]):
        self.messages = messages

    def get_messages(self, to: str) -> List[Message]:
        """retrieve messages for someone, and take them out of the network"""
        theirs = [m for m in self.messages if m.to == to]
        for m in theirs:
            self.messages.remove(m)
        return theirs

    def dispatch(self, msg: Message) -> None:
        """put the message into the network"""
        self.messages.append(msg)


def test_replication_one_server_simple_case():
    leader = Leader(
        name="S1", peers=["S2"], log=InMemoryLog([]), currentTerm=1, votedFor=None
    )
    follower = Follower(
        name="S2", log=InMemoryLog([]), currentTerm=1, votedFor=None
    )
    client_set = Message(frm="client.id", to="S1", cmd=ClientSetCommand("foo=1"))

    raftnet = FakeRaftNetwork([])
    raftnet.dispatch(client_set)

    clock_tick(leader, raftnet)
    clock_tick(follower, raftnet)
    assert follower.log.read()[-1].cmd == "foo=1"


def test_replication_multiple_servers_simple_case():
    peers = ["S2", "S3"]
    leader = Leader(
        name="S1", peers=peers, log=InMemoryLog([]), currentTerm=1, votedFor=None
    )
    f1 = Follower(name="S2", log=InMemoryLog([]), currentTerm=1, votedFor=None)
    f2 = Follower(name="S3", log=InMemoryLog([]), currentTerm=1, votedFor=None)

    client_set = Message(frm="client.id", to="S1", cmd=ClientSetCommand("foo=1"))

    raftnet = FakeRaftNetwork([])
    raftnet.dispatch(client_set)
    clock_tick(leader, raftnet)
    clock_tick(f1, raftnet)
    clock_tick(f2, raftnet)
    assert f1.log.read()[-1].cmd == "foo=1"
    assert f2.log.read()[-1].cmd == "foo=1"


def test_replication_backtracking():
    assert 0, 'todo'

    # IDEA:
    while raftnet.messages:
        for s in peers:
            clock_tick(s, raftnet)
