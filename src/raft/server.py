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
        self, name: str, log: Log, now: float,
        currentTerm: int, votedFor: Optional[str],
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
        print(f'{self.name} handling {msg.cmd.__class__.__name__} from {msg.frm}')
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
        log: Log,
        now: float,
        peers: List[str],
        currentTerm: int,
        votedFor: Optional[str],
    ):
        super().__init__(name, log, now, currentTerm, votedFor)
        self.peers = peers

        # Raft leader volatile state
        self.nextIndex = {
            server_name: self.log.lastLogIndex for server_name in self.peers
        }  # type: Dict[str, int]

        ## I am going to try and get backtracking working using only matchIndex
        ## so i am initializing it to lastLogIndex instead of 0
        ## TODO: i think this won't work when it comes to calculating commitIndex??
        self.matchIndex = {
            server_name: self.log.lastLogIndex for server_name in self.peers
        }  # type: Dict[str, int]


    def handle_message(self, msg: Message) -> None:
        print(f'{self.name} handling {msg.cmd.__class__.__name__} from {msg.frm}')
        if isinstance(msg.cmd, ClientSetCommand):
            self._handle_client_set(cmd=msg.cmd.cmd)

        if isinstance(msg.cmd, AppendEntriesSucceeded):
            self.matchIndex[msg.frm] = msg.cmd.matchIndex
            if self.matchIndex[msg.frm] < self.log.lastLogIndex:
                next_to_send = self.log.entry_at(self.matchIndex[msg.frm] + 1)
                prevLogIndex = self.matchIndex[msg.frm]
                prevLogTerm = self.log.entry_term(prevLogIndex)
                self.outbox.append(Message(frm=self.name, to=msg.frm, cmd=AppendEntries(
                    term=self.currentTerm,
                    leaderId=self.name,
                    prevLogIndex=prevLogIndex,
                    prevLogTerm=prevLogTerm,
                    leaderCommit=0,
                    entries=[next_to_send],
                )))

        if isinstance(msg.cmd, AppendEntriesFailed):
            self.matchIndex[msg.frm] -= 1
            to_resend = self.log.entry_at(self.matchIndex[msg.frm])
            print(f'{msg.frm} failed, resending entry at {self.matchIndex[msg.frm]}')
            prevLogIndex = self.matchIndex[msg.frm] - 1
            prevLogTerm = self.log.entry_term(prevLogIndex)
            self.outbox.append(Message(frm=self.name, to=msg.frm, cmd=AppendEntries(
                term=self.currentTerm,
                leaderId=self.name,
                prevLogIndex=prevLogIndex,
                prevLogTerm=prevLogTerm,
                leaderCommit=0,
                entries=[to_resend],
            )))

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
