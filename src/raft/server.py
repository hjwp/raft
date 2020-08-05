from typing import Dict, List, Optional
from raft.log import Log, Entry
from raft.messages import (
    Message,
    AppendEntries,
    AppendEntriesSucceeded,
    AppendEntriesFailed,
    ClientSetCommand,
)


class Server:
    def __init__(
        self, name: str, log: Log, currentTerm: int, votedFor: Optional[str],
    ):
        self.name = name
        self.outbox = []  # type: List[Message]

        # Raft persistent state
        self.log = log
        self.currentTerm = currentTerm
        self.votedFor = votedFor

        # Raft volatile state
        self.commitIndex = 0
        self.lastApplied = 0

    def handle_message(self, msg: Message):
        ...

    def clock_tick(self, now: float):
        ...


class Follower(Server):
    def handle_message(self, msg: Message) -> None:
        if isinstance(msg.cmd, AppendEntries):
            self._handle_append_entries(frm=msg.frm, cmd=msg.cmd)

    def _handle_append_entries(self, frm: str, cmd: AppendEntries) -> None:
        for entry in cmd.entries:
            success = self.log.add_entry(
                entry, cmd.prevLogIndex, cmd.prevLogTerm, cmd.leaderCommit
            )
            if not success:
                self.outbox.append(
                    Message(
                        frm=self.name,
                        to=frm,
                        cmd=AppendEntriesFailed(term=self.currentTerm),
                    )
                )
                return
        self.outbox.append(
            Message(
                frm=self.name,
                to=frm,
                cmd=AppendEntriesSucceeded(matchIndex=self.log.lastLogIndex),
            )
        )


class Leader(Server):
    def __init__(
        self,
        name: str,
        peers: List[str],
        log: Log,
        currentTerm: int,
        votedFor: Optional[str],
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

    def handle_message(self, msg: Message) -> None:
        if isinstance(msg.cmd, ClientSetCommand):
            self._handle_client_set(cmd=msg.cmd.cmd)
        if isinstance(msg.cmd, AppendEntriesSucceeded):
            self.matchIndex[msg.frm] = msg.cmd.matchIndex

    def _handle_client_set(self, cmd: str):
        prevLogIndex = self.log.lastLogIndex
        prevLogTerm = self.log.last_log_term
        new_entry = Entry(term=self.currentTerm, cmd=cmd)
        assert self.log.add_entry(
            entry=new_entry,
            prevLogIndex=prevLogIndex,
            prevLogTerm=prevLogTerm,
            leaderCommit=1,
        )
        print(f"server added {cmd} at position {prevLogIndex + 1}")
        ae = AppendEntries(
            term=self.currentTerm,
            leaderId=self.name,
            prevLogIndex=prevLogIndex,
            prevLogTerm=prevLogTerm,
            leaderCommit=0,
            entries=[new_entry],
        )
        self.outbox.extend(Message(frm=self.name, to=s, cmd=ae) for s in self.peers)
