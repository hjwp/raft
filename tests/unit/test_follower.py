import pytest
from raft.server import Follower, ELECTION_TIMEOUT_JITTER, MIN_ELECTION_TIMEOUT
from raft.log import InMemoryLog, Entry
from raft.messages import (
    AppendEntries,
    AppendEntriesSucceeded,
    AppendEntriesFailed,
    RequestVote,
    Message,
)


def test_append_entries_adds_to_local_log_and_returns_success_response():
    log = InMemoryLog([])
    s = Follower(
        name="S2",
        peers=["S1", "S2", "S3"],
        now=1,
        log=log,
        currentTerm=1,
        votedFor=None,
    )
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


def test_append_entries_with_no_entry_aka_heartbeat_at_zero():
    log = InMemoryLog([])
    s = Follower(
        name="S2",
        peers=["S1", "S2", "S3"],
        now=1,
        log=log,
        currentTerm=1,
        votedFor=None,
    )
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
                entries=[],
            ),
        )
    )
    assert s.log.read() == []
    expected_response = AppendEntriesSucceeded(matchIndex=0)
    assert s.outbox == [Message(frm="S2", to="S1", cmd=expected_response)]


def test_append_entries_with_no_entry_aka_heartbeat_at_nonzero():
    log = InMemoryLog([Entry(term=1, cmd="foo=1")])
    s = Follower(
        name="S2",
        peers=["S1", "S2", "S3"],
        now=1,
        log=log,
        currentTerm=1,
        votedFor=None,
    )
    s.handle_message(
        Message(
            frm="S1",
            to="S2",
            cmd=AppendEntries(
                term=1,
                leaderId="S1",
                prevLogIndex=1,
                prevLogTerm=1,
                leaderCommit=1,
                entries=[],
            ),
        )
    )
    expected_response = AppendEntriesSucceeded(matchIndex=1)
    assert s.outbox == [Message(frm="S2", to="S1", cmd=expected_response)]


def test_append_entries_failed_response():
    old_entries = [Entry(term=1, cmd="first=entry"), Entry(term=2, cmd="e=2")]
    log = InMemoryLog(old_entries)
    s = Follower(
        name="S2",
        peers=["S1", "S2", "S3"],
        now=1,
        log=log,
        currentTerm=2,
        votedFor=None,
    )
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


def test_append_entries_failed_response_to_heartbeat():
    old_entries = [Entry(term=1, cmd="first=entry"), Entry(term=2, cmd="e=2")]
    log = InMemoryLog(old_entries)
    s = Follower(
        name="S2",
        peers=["S1", "S2", "S3"],
        now=1,
        log=log,
        currentTerm=2,
        votedFor=None,
    )
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
                entries=[],
            ),
        )
    )
    assert s.log.read() == old_entries
    expected_response = AppendEntriesFailed(term=2)
    assert s.outbox == [Message(frm="S2", to="S1", cmd=expected_response)]


@pytest.mark.xfail
def test_clock_tick_does_nothing_by_default():
    term = 2
    s = Follower(
        name="S2",
        peers=["S1", "S2", "S3"],
        now=1,
        log=InMemoryLog([]),
        currentTerm=term,
        votedFor=None,
    )
    a_tiny_amount_of_time = 0.001
    s.clock_tick(a_tiny_amount_of_time)
    assert s.currentTerm == term
    assert s.outbox == []


@pytest.mark.xfail
def test_calls_election_if_clock_tick_past_election_timeout():
    log = [Entry(2, "foo=1"), Entry(3, "foo=2")]
    f = Follower(
        name="S2",
        peers=["S1", "S2", "S3"],
        now=1,
        log=InMemoryLog(log),
        currentTerm=3,
        votedFor=None,
    )
    a_tiny_amount_of_time = 0.001
    f.clock_tick(a_tiny_amount_of_time)
    assert f.outbox == []

    past_timeout = 1
    assert MIN_ELECTION_TIMEOUT + ELECTION_TIMEOUT_JITTER < past_timeout
    f.clock_tick(past_timeout)

    assert f.currentTerm == 4
    assert f.outbox == [
        Message(
            frm="S2",
            to=s,
            cmd=RequestVote(term=4, candidateId="S2", lastLogIndex=2, lastLogTerm=3),
        )
        for s in f.peers
    ]
