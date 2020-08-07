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
    peers = ["S1", "S2", "S3"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)
    assert s.matchIndex == {'S2': 0, 'S3': 0}
    assert s.nextIndex == {'S2': 3, 'S3': 3}


def test_handle_client_set_updates_local_log_and_puts_AppendEntries_in_outbox():
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)

    s.handle_message(Message(frm="client.id", to="S1", cmd=ClientSetCommand(guid='gaga', cmd="foo=bar")))
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
        Message(frm="S1", to=s, cmd=expected_appendentries) for s in peers if s != "S1"
    ]


def test_successful_appendentries_response_updates_matchIndex_last_entry_case():
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)

    s.matchIndex["S2"] = 1  # arbitrarily
    s.nextIndex["S2"] = 2
    s.handle_message(
        Message(frm="S2", to="S1", cmd=AppendEntriesSucceeded(matchIndex=2))
    )
    assert s.matchIndex["S2"] == 2
    assert s.nextIndex["S2"] == 3
    assert s.outbox == []


def test_successful_appendentries_cannot_take_nextIndex_past_end():
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)

    s.nextIndex["S2"] = 3
    s.handle_message(
        Message(frm="S2", to="S1", cmd=AppendEntriesSucceeded(matchIndex=2))
    )
    assert s.nextIndex["S2"] == 3


def test_duplicate_appendentries_responses_do_not_double_increment_index_counters():
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [
        Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2"), Entry(term=2, cmd='old=3')
    ]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)
    s.matchIndex["S2"] = 1  # arbitrarily
    s.nextIndex["S2"] = 2
    s.handle_message(
        Message(frm="S2", to="S1", cmd=AppendEntriesSucceeded(matchIndex=2))
    )
    assert s.matchIndex["S2"] == 2
    assert s.nextIndex["S2"] == 3
    s.handle_message(
        Message(frm="S2", to="S1", cmd=AppendEntriesSucceeded(matchIndex=2))
    )
    assert s.matchIndex["S2"] == 2
    assert s.nextIndex["S2"] == 3


def test_failed_appendentries_decrements_nextindex_and_adds_new_AppendEntries_to_outbox():
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)
    s.matchIndex["S2"] = 2  # arbitrarily
    s.nextIndex["S2"] = 2  # arbitrarily
    s.handle_message(Message(frm="S2", to="S1", cmd=AppendEntriesFailed(term=2)))
    assert s.matchIndex["S2"] == 2  # should not move
    assert s.nextIndex["S2"] == 1
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


def test_failed_appendentries_cannot_take_nextIndex_below_one():
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)
    s.nextIndex["S2"] = 1

    s.handle_message(Message(frm="S2", to="S1", cmd=AppendEntriesFailed(term=2)))
    assert s.nextIndex["S2"] == 1


@pytest.mark.xfail
def test_duplicate_failed_appendentries_do_not_double_decrement_or_double_reappend():
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)
    s.nextIndex["S2"] = 3
    s.matchIndex["S2"] = 2  # arbitrarily

    s.handle_message(Message(frm="S2", to="S1", cmd=AppendEntriesFailed(term=2)))
    assert s.matchIndex["S2"] == 2
    assert s.nextIndex["S2"] == 2

    s.handle_message(Message(frm="S2", to="S1", cmd=AppendEntriesFailed(term=2)))
    assert s.matchIndex["S2"] == 2
    assert s.nextIndex["S2"] == 2  # do we care?
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
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)
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
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)
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
        Message(frm="S1", to=s, cmd=expected_appendentries) for s in peers if s != "S1"
    ]


def test_heartbeat_is_custom_for_each_follower_based_on_nextIndex():
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)
    s.nextIndex['S2'] = 1
    s.nextIndex['S3'] = 2
    s.nextIndex['S4'] = 3
    s.nextIndex['S5'] = 3
    s.clock_tick(now=2)
    assert 2 - 1 > HEARTBEAT_FREQUENCY

    assert s.outbox == [
        Message(
            frm='S1', to='S2', cmd=AppendEntries(
            term=2,
            leaderId="S1",
            prevLogIndex=0,
            prevLogTerm=0,
            leaderCommit=0,
            entries=[],
        )),
        Message(
            frm='S1', to='S3', cmd=AppendEntries(
            term=2,
            leaderId="S1",
            prevLogIndex=1,
            prevLogTerm=1,
            leaderCommit=0,
            entries=[],
        )),
        Message(
            frm='S1', to='S4', cmd=AppendEntries(
            term=2,
            leaderId="S1",
            prevLogIndex=2,
            prevLogTerm=2,
            leaderCommit=0,
            entries=[],
        )),
        Message(
            frm='S1', to='S5', cmd=AppendEntries(
            term=2,
            leaderId="S1",
            prevLogIndex=2,
            prevLogTerm=2,
            leaderCommit=0,
            entries=[],
        )),
    ]

def test_heartbeat_only_appears_once_per_interval():
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=2, votedFor=None)
    s.clock_tick(1)
    s.outbox[:] = []  # clear outbox
    too_soon = 1 + HEARTBEAT_FREQUENCY / 2.0
    s.clock_tick(too_soon)
    assert s.outbox == []
    stilL_too_soon = 1 + HEARTBEAT_FREQUENCY - 0.001
    s.clock_tick(stilL_too_soon)
    assert s.outbox == []
    just_after = 1 + HEARTBEAT_FREQUENCY + 0.001
    s.clock_tick(just_after)
    assert len(s.outbox) == 4
    two_heartbeats_in_theory = 1 + HEARTBEAT_FREQUENCY * 2

    # test we track time since last heartbeat, rather than from t=0
    assert two_heartbeats_in_theory < (just_after + HEARTBEAT_FREQUENCY)
    s.clock_tick(two_heartbeats_in_theory)
    assert len(s.outbox) == 4

    next_one = just_after + HEARTBEAT_FREQUENCY + 0.001
    s.clock_tick(next_one)
    assert len(s.outbox) == 8


def test_becoming_follower_should_reset_matchindex_and_nextIndex():
    s = Leader(name="S1", now=1, log=InMemoryLog([]), peers=["S1", "S2"], currentTerm=1, votedFor=None)
    s.matchIndex["S2"] = 99
    s.nextIndex["S2"] = 99
    s._become_follower()
    assert s.matchIndex == {}
    assert s.nextIndex == {}


def test_updates_commitIndex_on_quorum_AppendEntriesSucceeded():
    peers = ["S1", "S2", "S3", "S4", "S5"]
    old_entries = [Entry(term=1, cmd="old=1"), Entry(term=2, cmd="old=2")]
    log = InMemoryLog(old_entries)
    s = Leader(name="S1", now=1, log=log, peers=peers, currentTerm=1, votedFor=None)
    assert s.commitIndex == 0
    s.handle_message(
        Message(frm="S2", to="S1", cmd=AppendEntriesSucceeded(matchIndex=1))
    )
    assert s.commitIndex == 0
    s.handle_message(
        Message(frm="S2", to="S1", cmd=AppendEntriesSucceeded(matchIndex=2))
    )
    assert s.commitIndex == 0
    s.handle_message(
        Message(frm="S3", to="S1", cmd=AppendEntriesSucceeded(matchIndex=1))
    )
    assert s.commitIndex == 1
