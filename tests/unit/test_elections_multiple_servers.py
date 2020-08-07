import pytest
from raft.adapters.network import FakeRaftNetwork
from raft.adapters.run_server import clock_tick
from raft.log import InMemoryLog, Entry
from raft.messages import Message, ClientSetCommand
from raft.server import Leader, Follower, Candidate, MIN_ELECTION_TIMEOUT
import figure_7

def make_follower(name, peers) -> Follower:
    return Follower(
        name=name,
        peers=peers,
        now=0,
        log=InMemoryLog([]),
        currentTerm=0,
        votedFor=None,
    )


def test_simple_election():
    peers = ["S1", "S2", "S3"]
    f1, f2, f3 = [make_follower(n, peers) for n in peers]

    raftnet = FakeRaftNetwork([])
    start = int(MIN_ELECTION_TIMEOUT * 1000) - 1
    for i in range(start, start * 2):
        print(f"*** --- CLOCK TIIIIICK {i} --- ***")
        clock_tick(f1, raftnet, i / 1000)
        clock_tick(f2, raftnet, i / 1000)
        clock_tick(f3, raftnet, i / 1000)

    assert any(isinstance(f, Leader) for f in [f1, f2, f3])

def test_figure_7():
    servers = figure_7.make_servers()
    del servers['l']   # oh noes, what will they do without a leader???

    raftnet = FakeRaftNetwork([])
    start = int(MIN_ELECTION_TIMEOUT * 1000) - 1
    for i in range(start, start * 3):
        # print(f"*** --- CLOCK TIIIIICK {i} --- ***")
        for _, s in servers.items():
            clock_tick(s, raftnet, i / 1000.0)

    for n, s in servers.items():
        print(f'Checking log for {s}: {s.log.read()}')
        terms = [e.term for e in s.log.read()]
        assert terms[:9] == list(map(int, '1114455666'))
