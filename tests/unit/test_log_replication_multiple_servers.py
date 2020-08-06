import pytest
from typing import List
from raft.adapters.run_server import clock_tick
from raft.log import InMemoryLog, Entry
from raft.messages import Message, ClientSetCommand
from raft.server import Leader, Follower


class FakeRaftNetwork:
    def __init__(self, messages: List[Message]):
        self._messages = messages

    def get_messages(self, to: str) -> List[Message]:
        """retrieve messages for someone, and take them out of the network"""
        theirs = [m for m in self._messages if m.to == to]
        for m in theirs:
            self._messages.remove(m)
        return theirs

    def dispatch(self, msg: Message) -> None:
        """put the message into the network"""
        self._messages.append(msg)


def test_replication_one_server_simple_case():
    leader = Leader(
        name="S1",
        now=1,
        log=InMemoryLog([]),
        peers=["S1", "S2"],
        currentTerm=1,
        votedFor=None,
    )
    follower = Follower(
        name="S2",
        peers=["S1", "S2"],
        now=1,
        log=InMemoryLog([]),
        currentTerm=1,
        votedFor=None,
    )
    client_set = Message(frm="client.id", to="S1", cmd=ClientSetCommand("foo=1"))

    raftnet = FakeRaftNetwork([])
    raftnet.dispatch(client_set)

    clock_tick(leader, raftnet, 1)
    clock_tick(follower, raftnet, 1)
    assert follower.log.read()[-1].cmd == "foo=1"


def test_replication_multiple_servers_simple_case():
    peers = ["S1", "S2", "S3"]
    leader = Leader(
        name="S1", now=1, log=InMemoryLog([]), peers=peers, currentTerm=1, votedFor=None
    )
    f1 = Follower(
        name="S2", peers=peers, now=1, log=InMemoryLog([]), currentTerm=1, votedFor=None
    )
    f2 = Follower(
        name="S3", peers=peers, now=1, log=InMemoryLog([]), currentTerm=1, votedFor=None
    )

    client_set = Message(frm="client.id", to="S1", cmd=ClientSetCommand("foo=1"))

    raftnet = FakeRaftNetwork([])
    raftnet.dispatch(client_set)
    clock_tick(leader, raftnet, 1)
    clock_tick(f1, raftnet, 1)
    clock_tick(f2, raftnet, 1)
    assert f1.log.read()[-1].cmd == "foo=1"
    assert f2.log.read()[-1].cmd == "foo=1"


def test_replication_backtracking():
    peers = ["S1", "S2", "S3"]
    leader_entries = [
        Entry(term=1, cmd="monkeys=1"),
        Entry(term=2, cmd="bananas=2"),
        Entry(term=2, cmd="turtles=3"),
    ]
    one_wrong_entry = [
        Entry(term=1, cmd="monkeys=1"),
        Entry(term=1, cmd="monkeys=2"),
    ]

    leader = Leader(
        name="S1",
        now=1,
        log=InMemoryLog(leader_entries),
        peers=peers,
        currentTerm=2,
        votedFor=None,
    )
    f1 = Follower(
        name="S2", peers=peers, now=1, log=InMemoryLog([]), currentTerm=2, votedFor=None
    )
    f2 = Follower(
        name="S3",
        peers=peers,
        now=1,
        log=InMemoryLog(one_wrong_entry),
        currentTerm=2,
        votedFor=None,
    )

    client_set = Message(frm="client.id", to="S1", cmd=ClientSetCommand("gherkins=4"))

    raftnet = FakeRaftNetwork([])
    raftnet.dispatch(client_set)

    for i in range(1, 11):  # IDEA: while raftnet.messages?
        print(f"*** --- CLOCK TIIIIICK {i} --- ***")
        clock_tick(leader, raftnet, i)
        clock_tick(f1, raftnet, i)
        clock_tick(f2, raftnet, i)

    expected = leader_entries + [Entry(term=2, cmd="gherkins=4")]

    assert leader.log.read() == expected
    assert f1.log.read() == expected
    assert f2.log.read() == expected
