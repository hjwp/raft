from raft.server import Server, Leader
from raft.log import InMemoryLog, Entry
from raft.messages import AppendEntries, Message, ClientSetCommand


def test_handle_client_set_updates_local_log_and_puts_AppendEntries_in_outbox():
    peers = ["S2", "S3", "S4", "S5"]
    log = InMemoryLog([])
    s = Leader(
        name="S1", peers=peers, log=log, currentTerm=1, votedFor=None
    )
    s.handle_message(Message(frm='client.id', to='S1', cmd=ClientSetCommand('foo=bar')))
    expected_entry = Entry(term=1, cmd="foo=bar")
    assert s.log.read() == [expected_entry]
    expected_appendentries = AppendEntries(
        term=1,
        leaderId="S1",
        prevLogIndex=0,
        prevLogTerm=0,
        leaderCommit=0,
        entries=[expected_entry],
    )
    assert s.outbox == [
        Message(frm="S1", to=s, cmd=expected_appendentries)
        for s in peers
    ]
