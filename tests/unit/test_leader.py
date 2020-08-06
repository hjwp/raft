import pytest
from raft.server import Server, Leader, HEARTBEAT_FREQUENCY
from raft.log import InMemoryLog, Entry
from raft.messages import (
    AppendEntries,
    AppendEntriesSucceeded,
    AppendEntriesFailed,
    Message,
    ClientSetCommand,
)

def test_init():
    peers = ["S2", "S3"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", log=log, now=1, peers=peers, currentTerm=2, votedFor=None)
    assert s.matchIndex == {'S2': 0, 'S3': 0}
    assert s.nextIndex == {'S2': 3, 'S3': 3}


def test_handle_client_set_updates_local_log_and_puts_AppendEntries_in_outbox():
    peers = ["S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", log=log, now=1, peers=peers, currentTerm=2, votedFor=None)

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


def test_successful_appendentries_response_updates_matchIndex_last_entry_case():
    peers = ["S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", log=log, now=1, peers=peers, currentTerm=2, votedFor=None)

    s.matchIndex["S2"] == 1  # arbitrarily
    s.handle_message(
        Message(frm="S2", to="S1", cmd=AppendEntriesSucceeded(matchIndex=2))
    )
    assert s.matchIndex["S2"] == 2
    assert s.outbox == []


def test_duplicate_appendentries_responses_do_not_double_increment_matchindex():
    peers = ["S2", "S3", "S4", "S5"]
    old_entries = [
        Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2"), Entry(term=2, cmd='old=3')
    ]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", log=log, now=1, peers=peers, currentTerm=2, votedFor=None)
    s.matchIndex["S2"] == 1  # arbitrarily
    s.handle_message(
        Message(frm="S2", to="S1", cmd=AppendEntriesSucceeded(matchIndex=2))
    )
    assert s.matchIndex["S2"] == 2
    s.handle_message(
        Message(frm="S2", to="S1", cmd=AppendEntriesSucceeded(matchIndex=2))
    )
    assert s.matchIndex["S2"] == 2


def test_failed_appendentries_decrements_matchindex_and_adds_new_AppendEntries_to_outbox():
    peers = ["S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", log=log, now=1, peers=peers, currentTerm=2, votedFor=None)
    s.matchIndex["S2"] = 2  # arbitrarily
    s.handle_message(Message(frm="S2", to="S1", cmd=AppendEntriesFailed(term=2)))
    assert s.matchIndex["S2"] == 1
    assert s.outbox == [
        Message(
            frm="S1",
            to="S2",
            cmd=AppendEntries(
                term=2,
                leaderId="S1",
                prevLogIndex=0,
                prevLogTerm=0,
                leaderCommit=0,
                entries=[old_entries[0]],
            ),
        )
    ]

@pytest.mark.xfail
def test_duplicate_failed_appendentries_do_not_double_decrement_or_double_reappend():
    peers = ["S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", log=log, now=1, peers=peers, currentTerm=2, votedFor=None)
    s.matchIndex["S2"] = 2  # arbitrarily
    s.handle_message(Message(frm="S2", to="S1", cmd=AppendEntriesFailed(term=2)))
    assert s.matchIndex["S2"] == 1
    s.handle_message(Message(frm="S2", to="S1", cmd=AppendEntriesFailed(term=2)))
    assert s.matchIndex["S2"] == 1
    assert s.outbox == [
        Message(
            frm="S1",
            to="S2",
            cmd=AppendEntries(
                term=2,
                leaderId="S1",
                prevLogIndex=0,
                prevLogTerm=0,
                leaderCommit=0,
                entries=[old_entries[0]],
            ),
        )
    ]

def test_successful_appendentries_response_adds_AppendEntries_if_matchIndex_lower_than_lastIndex():
    peers = ["S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", log=log, now=1, peers=peers, currentTerm=2, votedFor=None)
    s.matchIndex["S2"] == 0  # arbitrarily
    s.handle_message(
        Message(frm="S2", to="S1", cmd=AppendEntriesSucceeded(matchIndex=1))
    )
    assert s.matchIndex["S2"] == 1
    assert s.outbox == [
        Message(
            frm="S1",
            to="S2",
            cmd=AppendEntries(
                term=2,
                leaderId="S1",
                prevLogIndex=1,
                prevLogTerm=1,
                leaderCommit=0,
                entries=[old_entries[1]],
            ),
        )
    ]


def test_clock_tick_gives_first_heartbeat():
    peers = ["S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", log=log, now=1, peers=peers, currentTerm=2, votedFor=None)
    s.clock_tick(now=2)
    assert 2 - 1 > HEARTBEAT_FREQUENCY

    expected_appendentries = AppendEntries(
        term=2,
        leaderId="S1",
        prevLogIndex=2,
        prevLogTerm=2,
        leaderCommit=0,
        entries=[],
    )
    assert s.outbox == [
        Message(frm="S1", to=s, cmd=expected_appendentries) for s in peers
    ]

