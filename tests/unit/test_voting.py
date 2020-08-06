import pytest
from raft.server import Follower
from raft.log import InMemoryLog
from raft.messages import Message, RequestVote, VoteDenied

def make_follower() -> Follower:
    return Follower(
        name="S1",
        peers=["S1", "S2", "S3"],
        now=0,
        log=InMemoryLog([]),
        currentTerm=10,
        votedFor=None,
    )

def make_RequestVote(term: int, lastLogIndex: int, lastLogTerm: int) -> Message:
    return Message(frm="S2", to="S1", cmd=RequestVote(term=term, candidateId="S2", lastLogIndex=lastLogIndex, lastLogTerm=lastLogTerm))

def test_deny_vote_if_candidate_term_too_old():
    s = make_follower()
    s.handle_message(make_RequestVote(term=s.currentTerm -1, lastLogIndex=s.log.lastLogIndex + 1, lastLogTerm=s.log.last_log_term))
    assert s.outbox[0].cmd == VoteDenied(term=s.currentTerm)

if False:
    def test_deny_vote_if_lastLogTerm_is_too_low():
        assert 0, 'todo'

    def test_deny_vote_if_lastLogIndex_is_too_low():
        assert 0, 'todo'

    def test_deny_vote_if_already_voted_for_someone_else():
        assert 0, 'todo'

    def test_grant_vote_again_if_already_voted_for_same_candidate():
        assert 0, 'todo'

