import pytest
from raft.server import Follower
from raft.log import InMemoryLog
from raft.messages import Message, RequestVote, VoteGranted, VoteDenied

def make_follower(votedFor=None) -> Follower:
    return Follower(
        name="S1",
        peers=["S1", "S2", "S3"],
        now=0,
        log=InMemoryLog([]),
        currentTerm=10,
        votedFor=votedFor,
    )

def make_RequestVote(term: int, lastLogIndex: int, lastLogTerm: int) -> Message:
    return Message(frm="S2", to="S1", cmd=RequestVote(term=term, candidateId="S2", lastLogIndex=lastLogIndex, lastLogTerm=lastLogTerm))

def test_deny_vote_if_candidate_term_too_old():
    s = make_follower()
    s.handle_message(make_RequestVote(term=s.currentTerm -1, lastLogIndex=s.log.lastLogIndex + 1, lastLogTerm=s.log.last_log_term))
    [msg] = s.outbox
    assert msg.cmd == VoteDenied(term=s.currentTerm)

def test_deny_vote_if_lastLogTerm_is_too_low():
    s = make_follower()
    s.handle_message(make_RequestVote(term=s.currentTerm, lastLogIndex=s.log.lastLogIndex + 1, lastLogTerm=s.log.last_log_term - 1))
    [msg] = s.outbox
    assert msg.cmd == VoteDenied(term=s.currentTerm)

def test_deny_vote_if_lastLogIndex_is_too_low():
    s = make_follower()
    s.handle_message(make_RequestVote(term=s.currentTerm, lastLogIndex=s.log.lastLogIndex - 1, lastLogTerm=s.log.last_log_term - 1))
    [msg] = s.outbox
    assert msg.cmd == VoteDenied(term=s.currentTerm)


def test_deny_vote_if_already_voted_for_someone_else_in_this_term():
    s = make_follower(votedFor="S3")
    s.handle_message(make_RequestVote(term=s.currentTerm, lastLogIndex=s.log.lastLogIndex + 1, lastLogTerm=s.log.last_log_term + 1))
    [msg] = s.outbox
    assert msg.cmd == VoteDenied(term=s.currentTerm)


def test_grant_vote_if_term_greater_and_logindex_greater_and_lastlogterm_greater():
    s = make_follower()
    s.handle_message(make_RequestVote(term=s.currentTerm + 1, lastLogIndex=s.log.lastLogIndex + 1, lastLogTerm=s.log.last_log_term + 1))
    [msg] = s.outbox
    assert msg.cmd == VoteGranted()


def test_grant_vote_again_if_already_voted_for_same_candidate():
    s = make_follower(votedFor="S2")
    s.handle_message(make_RequestVote(term=s.currentTerm + 1, lastLogIndex=s.log.lastLogIndex + 1, lastLogTerm=s.log.last_log_term + 1))
    [msg] = s.outbox
    assert msg.cmd == VoteGranted()


def test_can_grant_vote_for_same_request_term():
    s = make_follower()
    s.handle_message(make_RequestVote(term=s.currentTerm, lastLogIndex=s.log.lastLogIndex + 1, lastLogTerm=s.log.last_log_term + 1))
    [msg] = s.outbox
    assert msg.cmd == VoteGranted()

def test_can_grant_vote_for_same_lastLogTerm():
    s = make_follower()
    s.handle_message(make_RequestVote(term=s.currentTerm + 1, lastLogIndex=s.log.lastLogIndex + 1, lastLogTerm=s.log.last_log_term))
    [msg] = s.outbox
    assert msg.cmd == VoteGranted()
