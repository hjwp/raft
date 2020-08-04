from raft.server import Server, Follower
from raft.log import InMemoryLog, Entry
from raft.messages import AppendEntries, AppendEntriesResponse, Message


def test_append_entries_adds_to_local_log_and_returns_response():
    log = InMemoryLog([])
    s = Follower(name="S2", log=log, currentTerm=1, votedFor=None)
    new_entry = Entry(term=1, cmd="foo=bar")
    s.handle_message(
        Message(
            to="S2",
            cmd=AppendEntries(
                term=1,
                leaderId="S1",
                prevLogIndex=0,
                prevLogTerm=0,
                leaderCommit=0,
                entries=[new_entry],
            ),
        )
    )
    assert s.log.read() == [new_entry]
    expected_response = AppendEntriesResponse(frm="S2", term=1, success=True)
    assert s.outbox == [Message(to="S1", cmd=expected_response)]
