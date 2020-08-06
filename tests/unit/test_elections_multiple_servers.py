import pytest
from raft.adapters.network import FakeRaftNetwork
from raft.adapters.run_server import clock_tick
from raft.log import InMemoryLog, Entry
from raft.messages import Message, ClientSetCommand
from raft.server import Leader, Follower, Candidate

def make_follower(name, peers) -> Follower:
    return Follower(
        name=name,
        peers=peers,
        now=0,
        log=InMemoryLog([]),
        currentTerm=0,
        votedFor=None,
    )


@pytest.mark.xfail
def test_simple_election():
    peers = ["S1", "S2", "S3"]
    f1, f2, f3 = [make_follower(n, peers) for n in peers]

    raftnet = FakeRaftNetwork([])
    for i in range(1, 11):  # IDEA: while raftnet.messages?
        print(f"*** --- CLOCK TIIIIICK {i} --- ***")
        clock_tick(f1, raftnet, i)
        clock_tick(f2, raftnet, i)
        clock_tick(f3, raftnet, i)

    assert any(isinstance(f, Leader) for f in [f1, f2, f3])

