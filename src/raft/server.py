from typing import Dict, List, Optional
from raft.log import Log, Entry
from raft.messages import Message, AppendEntries


class Server:
    def __init__(
        self, name: str, log: Log, currentTerm: int, votedFor: Optional[str],
    ):
        self.name = name

        # Raft persistent state
        self.log = log
        self.currentTerm = currentTerm
        self.votedFor = votedFor

        # Raft volatile state
        self.commitIndex = 0
        self.lastApplied = 0


class Leader(Server):
    def __init__(
        self, name: str, peers: List[str], log: Log, currentTerm: int, votedFor: str
    ):
        super().__init__(name, log, currentTerm, votedFor)
        self.peers = peers

        # Raft leader volatile state
        self.nextIndex = {
            server_name: self.log.lastLogIndex for server_name in self.peers
        }  # type: Dict[str, int]
        self.matchIndex = {
            server_name: 0 for server_name in self.peers
        }  # type: Dict[str, int]
        self.outbox = []  # type: List[Message]

    def handle_client_set(self, client_id: str, cmd: str):
        prevLogIndex = self.log.lastLogIndex
        prevLogTerm = self.log.last_log_term
        new_entry = Entry(term=self.currentTerm, cmd=cmd)
        assert self.log.add_entry(
            entry=new_entry, prevLogIndex=0, prevLogTerm=12, leaderCommit=1
        )
        ae = AppendEntries(
            term=self.currentTerm,
            leaderId=self.name,
            prevLogIndex=prevLogIndex,
            prevLogTerm=prevLogTerm,
            leaderCommit=0,
            entries=[new_entry],
        )
        self.outbox.extend(Message(to=s, cmd=ae) for s in self.peers)
