from raft.server import Server, Leader
from raft.log import InMemoryLog, Entry
from raft.messages import (
    AppendEntries,
    AppendEntriesSucceeded,
    AppendEntriesFailed,
    Message,
    ClientSetCommand,
)


def test_handle_client_set_updates_local_log_and_puts_AppendEntries_in_outbox():
    peers = ["S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", peers=peers, log=log, currentTerm=2, votedFor=None)
    s.handle_message(Message(frm="client.id", to="S1", cmd=ClientSetCommand("foo=bar")))
    expected_entry = Entry(term=2, cmd="foo=bar")
    assert s.log.read() == old_entries + [expected_entry]
    expected_appendentries = AppendEntries(
        term=2,
        leaderId="S1",
        prevLogIndex=2,
        prevLogTerm=2,
        leaderCommit=0,
        entries=[expected_entry],
    )
    assert s.outbox == [
        Message(frm="S1", to=s, cmd=expected_appendentries) for s in peers
    ]


def test_successful_appendentries_response_increments_matchindex():
    peers = ["S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", peers=peers, log=log, currentTerm=2, votedFor=None)
    s.handle_message(
        Message(frm="S2", to="S1", cmd=AppendEntriesSucceeded(matchIndex=2))
    )
    assert s.matchIndex["S2"] == 2


import pytest


@pytest.mark.xfail()
def test_failed_appendentries_decrements_matchindex_and_adds_new_AppendEntries_to_outbox():
    assert 0, "todo"


@pytest.mark.xfail()
def test_successful_appendentries_response_when_follower_still_catching_up():
    assert 0, "todo"
