import pytest
from typing import List
from raft.adapters.run_server import clock_tick
from raft.log import InMemoryLog, Entry
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


@pytest.mark.xfail()
def test_replication_backtracking():
    peers = ["S2", "S3"]
    leader_entries = [
        Entry(term=1, cmd='monkeys=1'),
        Entry(term=2, cmd='bananas=2'),
        Entry(term=2, cmd='turtles=3'),
    ]
    one_wrong_entry = [
        Entry(term=1, cmd='monkeys=1'),
        Entry(term=1, cmd='monkeys=2'),
    ]


    leader = Leader(
        name="S1", peers=peers, log=InMemoryLog(leader_entries), currentTerm=2, votedFor=None
    )
    f1 = Follower(name="S2", log=InMemoryLog([]), currentTerm=2, votedFor=None)
    f2 = Follower(name="S3", log=InMemoryLog(one_wrong_entry), currentTerm=2, votedFor=None)

    client_set = Message(frm="client.id", to="S1", cmd=ClientSetCommand("gherkins=4"))

    raftnet = FakeRaftNetwork([])
    raftnet.dispatch(client_set)
    for _ in range(100):  # IDEA: while raftnet.messages?
        clock_tick(leader, raftnet)
        clock_tick(f1, raftnet)
        clock_tick(f2, raftnet)
    expected = leader_entries + [Entry(term=2, cmd='gherkins=4')]

    assert leader.log.read() == expected
    assert f1.log.read() == expected
    assert f2.log.read() == expected
