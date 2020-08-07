import pytest
from raft.log import InMemoryLog
from raft.server import Leader, Follower, Candidate
from raft.messages import Message, AppendEntries, AppendEntriesFailed, RequestVote, VoteDenied

some_messages = [
    Message(frm="S2", to="S1", cmd=AppendEntries(term=5, leaderId="S2", prevLogIndex=22, prevLogTerm=4, entries=[], leaderCommit=9)),
    Message(frm="S2", to="S1", cmd=AppendEntriesFailed(term=5)),
    Message(frm="S2", to="S1", cmd=RequestVote(term=5, candidateId="S2", lastLogIndex=22, lastLogTerm=4)),
    Message(frm="S2", to="S1", cmd=VoteDenied(term=5)),
]
@pytest.mark.parametrize('server_class', [Leader, Follower, Candidate])
@pytest.mark.parametrize('msg', some_messages)
def test_messages_with_higher_term_should_convert_to_follower(server_class, msg):
    s = server_class("S1", peers=["S1", "S2", "S3"], now=0, log=InMemoryLog([]), currentTerm=4, votedFor="S3")
    s.handle_message(msg)
    assert s.currentTerm == 5
    assert isinstance(s, Follower)
    assert s.votedFor == None

@pytest.mark.parametrize('server_class', [Leader, Follower, Candidate])
def test_clock_tick_stores_time(server_class):
    s = server_class("S1", peers=["S1", "S2", "S3"], now=0, log=InMemoryLog([]), currentTerm=4, votedFor=None)
    assert s.now == 0
    s.clock_tick(3)
    assert s.now == 3
