import pytest
from raft.server import Follower, Leader, Candidate
from raft.log import InMemoryLog, Entry
from raft.messages import Message, RequestVote, VoteGranted, VoteDenied

def make_candidate(peers=None) -> Candidate:
    if peers is None:
        peers = ["S1", "S2", "S3", "S4", "S5"]
    c = Follower(
        name="S1",
        peers=peers,
        now=0,
        log=InMemoryLog([Entry(1, "foo=1"), Entry(1, "foo=2")]),
        currentTerm=10,
        votedFor=None,
    )
    c._become_candidate()
    return c

def test_votes_granted_below_quorum_do_not_have_immediate_effect():
    c = make_candidate()
    c.handle_message(Message(frm="S2", to="S1", cmd=VoteGranted()))
    assert isinstance(c, Candidate)


def test_becomes_leader_on_first_vote_to_go_above_quorum():
    c = make_candidate()
    c.handle_message(Message(frm="S2", to="S1", cmd=VoteGranted()))
    assert isinstance(c, Candidate)
    c.handle_message(Message(frm="S3", to="S1", cmd=VoteGranted()))
    assert isinstance(c, Leader)

def test_becomes_leader_on_first_vote_in_three_servers_case():
    c = make_candidate(peers=["S1", "S2", "S3"])
    c.handle_message(Message(frm="S2", to="S1", cmd=VoteGranted()))
    assert isinstance(c, Leader)

def test_becoming_leader_resets_leader_state_matchindex_and_nextindex():
    c = make_candidate(peers=["S1", "S2", "S3"])
    # maybe these are hanging around from previous state somehow
    c.matchIndex = {"S1": 1, "S2": 2, "S3": 3}
    c.nextIndex = {"S1": 1, "S2": 2, "S3": 3}
    c.handle_message(Message(frm="S2", to="S1", cmd=VoteGranted()))
    assert isinstance(c, Leader)
    c.matchIndex = {"S1": 0, "S2": 0, "S3": 0}
    c.nextIndex = {"S1": 3, "S2": 3, "S3": 3}
