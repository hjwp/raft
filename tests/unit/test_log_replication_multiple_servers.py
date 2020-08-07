import pytest
from typing import List
from raft.adapters.network import FakeRaftNetwork
from raft.adapters.run_server import clock_tick
from raft.log import InMemoryLog, Entry
from raft.messages import Message, ClientSetCommand
from raft.server import Leader, Follower, HEARTBEAT_FREQUENCY

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
        clock_tick(leader, raftnet, 1 + i / 100.0)
        clock_tick(f1, raftnet, 1 + i / 100.0)
        clock_tick(f2, raftnet, 1 + i / 100.0)

    expected = leader_entries + [Entry(term=2, cmd="gherkins=4")]

    assert leader.log.read() == expected
    assert f1.log.read() == expected
    assert f2.log.read() == expected


def test_figure_seven_from_paper():
    logs_from_paper_str = '''
        l,1114455666
        a,111445566
        b,1114
        c,11144556666
        d,111445566677
        e,1114444
        f,11122233333
    '''
    servers = {}
    peers = [c for c in 'labcdef']
    for line in logs_from_paper_str.strip().splitlines():
        name, _, entries = line.strip().partition(',')
        log = InMemoryLog([
            Entry(term=int(c), cmd=f'foo={c}')
            for c in entries
        ])
        args = dict(
            name=name, peers=peers, now=0, log=log, currentTerm=int(entries[-1]), votedFor=None
        )
        if name == 'l':
            servers[name] = Leader(**args)
        else:
            servers[name] = Follower(**args)
    print(servers)

    raftnet = FakeRaftNetwork([])
    one_heartbeat_in = HEARTBEAT_FREQUENCY + 0.0001

    for i in range(1, 100):
        print(f"*** --- CLOCK TIIIIICK {i} --- ***")
        for _, s in servers.items():
            clock_tick(s, raftnet, one_heartbeat_in + i / 1000.0)

    for n, s in servers.items():
        print(f'Checking log for server {n}: {s.log.read()}')
        terms = [e.term for e in s.log.read()]
        assert terms[:10] == list(map(int, '1114455666'))
