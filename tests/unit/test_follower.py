from raft.server import Server, Follower
from raft.log import InMemoryLog, Entry
from raft.messages import (
    AppendEntries,
    AppendEntriesSucceeded,
    AppendEntriesFailed,
    Message,
)


def test_append_entries_adds_to_local_log_and_returns_success_response():
    log = InMemoryLog([])
    s = Follower(name="S2", log=log, now=1, currentTerm=1, votedFor=None)
    new_entry = Entry(term=1, cmd="foo=bar")
    s.handle_message(
        Message(
            frm="S1",
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
    expected_response = AppendEntriesSucceeded(matchIndex=1)
    assert s.outbox == [Message(frm="S2", to="S1", cmd=expected_response)]


def test_append_entries_failed_response():
    old_entries = [Entry(term=1, cmd="first=entry"), Entry(term=2, cmd="e=2")]
    log = InMemoryLog(old_entries)
    s = Follower(name="S2", log=log, now=1, currentTerm=2, votedFor=None)
    new_entry = Entry(term=1, cmd="term=wrong")
    s.handle_message(
        Message(
            frm="S1",
            to="S2",
            cmd=AppendEntries(
                term=2,
                leaderId="S1",
                prevLogIndex=2,
                prevLogTerm=1,
                leaderCommit=0,
                entries=[new_entry],
            ),
        )
    )
    assert s.log.read() == old_entries
    expected_response = AppendEntriesFailed(term=2)
    assert s.outbox == [Message(frm="S2", to="S1", cmd=expected_response)]
