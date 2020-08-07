import pytest
from raft.adapters.network import FakeRaftNetwork
from raft.adapters.run_server import clock_tick
from raft.log import InMemoryLog, Entry
from raft.messages import Message, ClientSetCommand, ClientSetSucceeded
from raft.server import Leader, Follower, HEARTBEAT_FREQUENCY


@pytest.mark.xfail
def test_client_gets_response_but_only_when_new_entry_is_on_a_majority_of_servers():
    peers = ["S1", "S2", "S3"]
    leader = Leader(
        name="S1",
        now=1,
        log=InMemoryLog([Entry(term=1, cmd='foo=old1'), Entry(term=1, cmd='foo=old2')]),
        peers=peers,
        currentTerm=1,
        votedFor=None,
    )
    f1 = Follower(
        name="S2",
        peers=peers,
        now=1,
        log=InMemoryLog([]),
        currentTerm=1,
        votedFor=None,
    )
    f2 = Follower(
        name="S3",
        peers=peers,
        now=1,
        log=InMemoryLog([]),
        currentTerm=1,
        votedFor=None,
    )
    client_set = Message(frm="client.id", to="S1", cmd=ClientSetCommand(guid='gooey', cmd="foo=new"))

    raftnet = FakeRaftNetwork([])
    raftnet.dispatch(client_set)

    for i in range(1, 11):
        print(f"*** --- CLOCK TIIIIICK {i} --- ***")
        clock_tick(leader, raftnet, 1 + i / 100.0)
        clock_tick(f1, raftnet, 1 + i / 100.0)
        clock_tick(f2, raftnet, 1 + i / 100.0)
        if (
            (f1.log.read() and f1.log.read()[-1].cmd != 'foo=new')
            and 
            (f2.log.read() and f2.log.read()[-1].cmd != 'foo=new')
        ):
            # no quorum yet
            assert not [m for m in raftnet._messages if m.to == 'client.id']

    assert f1.log.read()[-1].cmd == 'foo=new'
    assert f2.log.read()[-1].cmd == 'foo=new'

    [response] = raftnet.get_messages('client.id')
    assert response.cmd == ClientSetSucceeded(guid='gooey')
