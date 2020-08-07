import random
from typing import Dict, List, Optional
from raft.log import Log, Entry
from raft.messages import (
    Message,
    AppendEntries,
    AppendEntriesSucceeded,
    AppendEntriesFailed,
    ClientSetCommand,
    RequestVote,
    VoteGranted,
    VoteDenied,
)

HEARTBEAT_FREQUENCY = 0.02
MIN_ELECTION_TIMEOUT = 0.15
ELECTION_TIMEOUT_JITTER = 0.15


class Server:
    def __init__(
        self,
        name: str,
        peers: List[str],
        now: float,
        log: Log,
        currentTerm: int,
        votedFor: Optional[str],
    ):
        self.name = name
        self.peers = peers
        self.now = now
        self._last_heartbeat = 0  # type: float
        self._reset_election_timeout()
        self.outbox = []  # type: List[Message]

        # Raft persistent state
        self.log = log
        self.currentTerm = currentTerm
        self.votedFor = votedFor

        # Raft volatile state
        self.commitIndex = 0
        self.lastApplied = 0

    def __repr__(self):
        return f'<{self.__class__.__name__}: term={self.currentTerm}, lastLogIndex={self.log.lastLogIndex}>'

    def _reset_election_timeout(self) -> None:
        jitter = random.randint(0, int(ELECTION_TIMEOUT_JITTER * 1000)) / 1000.0
        self._election_timeout = self.now + MIN_ELECTION_TIMEOUT + jitter

    def handle_message(self, msg: Message) -> None:
        print(f"{self.name} handling {msg}")
        if hasattr(msg.cmd, 'term') and msg.cmd.term > self.currentTerm:
            self.currentTerm = msg.cmd.term
            self.votedFor = None
            self._become_follower()
        self._handle_message(msg)

    def _handle_message(self, msg: Message) -> None:
        raise NotImplementedError

    def clock_tick(self, now: float):
        raise NotImplementedError

    def _become_follower(self) -> None:
        print(f'** {self.name} is becoming a Follower **')
        self.__class__ = Follower



class Leader(Server):
    def __init__(
        self,
        name: str,
        peers: List[str],
        now: float,
        log: Log,
        currentTerm: int,
        votedFor: Optional[str],
    ):
        super().__init__(name, peers, now, log, currentTerm, votedFor)
        self._setup_follower_tracking_indexes()

    def _setup_follower_tracking_indexes(self) -> None:
        # Raft leader volatile state
        self.nextIndex = {
            server_name: self.log.lastLogIndex + 1 for server_name in self.peers if server_name != self.name
        }  # type: Dict[str, int]
        self.matchIndex = {
            server_name: 0 for server_name in self.peers if server_name != self.name
        }  # type: Dict[str, int]

    def _heartbeat_for(self, follower) -> AppendEntries:
        print(f'making heartbeat for {follower}')
        prevLogIndex = self.nextIndex[follower] - 1
        prevLogTerm = self.log.entry_term(prevLogIndex)
        return AppendEntries(
            term=self.currentTerm,
            leaderId=self.name,
            prevLogIndex=prevLogIndex,
            prevLogTerm=prevLogTerm,
            leaderCommit=0,
            entries=[],
        )

    def _next_entry_for(self, follower) -> AppendEntries:
        prevLogIndex = self.nextIndex[follower] - 1
        prevLogTerm = self.log.entry_term(prevLogIndex)
        entry = self.log.entry_at(self.nextIndex[follower])
        return AppendEntries(
            term=self.currentTerm,
            leaderId=self.name,
            prevLogIndex=prevLogIndex,
            prevLogTerm=prevLogTerm,
            leaderCommit=0,
            entries=[entry],
        )

    def clock_tick(self, now: float) -> None:
        self.now = now
        if self.now > (self._last_heartbeat + HEARTBEAT_FREQUENCY):
            self._last_heartbeat = self.now
            self.outbox.extend(
                Message(frm=self.name, to=s, cmd=self._heartbeat_for(s))
                for s in self.peers
                if s != self.name
            )

    def _handle_message(self, msg: Message) -> None:
        if isinstance(msg.cmd, ClientSetCommand):
            self._handle_client_set(cmd=msg.cmd.cmd)

        if isinstance(msg.cmd, AppendEntriesSucceeded):
            self.matchIndex[msg.frm] = msg.cmd.matchIndex
            self.nextIndex[msg.frm] = msg.cmd.matchIndex + 1
            if self.matchIndex[msg.frm] < self.log.lastLogIndex:
                next_to_send = self.log.entry_at(self.matchIndex[msg.frm] + 1)
                prevLogIndex = self.matchIndex[msg.frm]
                prevLogTerm = self.log.entry_term(prevLogIndex)
                self.outbox.append(
                    Message(
                        frm=self.name,
                        to=msg.frm,
                        cmd=AppendEntries(
                            term=self.currentTerm,
                            leaderId=self.name,
                            prevLogIndex=prevLogIndex,
                            prevLogTerm=prevLogTerm,
                            leaderCommit=0,
                            entries=[next_to_send],
                        ),
                    )
                )

        if isinstance(msg.cmd, AppendEntriesFailed):
            self.nextIndex[msg.frm] = max(self.nextIndex[msg.frm] - 1, 1)
            index_to_resend = self.nextIndex[msg.frm]
            print(f"{msg.frm} failed, resending entry at {index_to_resend}")
            prevLogIndex = index_to_resend - 1
            prevLogTerm = self.log.entry_term(prevLogIndex)
            self.outbox.append(
                Message(
                    frm=self.name,
                    to=msg.frm,
                    cmd=AppendEntries(
                        term=self.currentTerm,
                        leaderId=self.name,
                        prevLogIndex=prevLogIndex,
                        prevLogTerm=prevLogTerm,
                        leaderCommit=0,
                        entries=[self.log.entry_at(index_to_resend)],
                    ),
                )
            )

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
        self.outbox.extend(
            Message(frm=self.name, to=s, cmd=ae) for s in self.peers if s != self.name
        )



class Follower(Server):

    def clock_tick(self, now: float):
        self.now = now
        if self.now > self._election_timeout:
            print(f'election timeout!  {self.now} was greater than {self._election_timeout}')
            self._reset_election_timeout()
            self._become_candidate()


    def _handle_message(self, msg: Message) -> None:
        if isinstance(msg.cmd, AppendEntries):
            kvcmd = msg.cmd.entries[0].cmd if msg.cmd.entries else "HeArtBeAt"
            self._handle_AppendEntries(frm=msg.frm, cmd=msg.cmd)

        if isinstance(msg.cmd, RequestVote):
            self._handle_RequestVote(frm=msg.frm, cmd=msg.cmd)

    def _handle_RequestVote(self, frm: str, cmd: RequestVote) -> None:
        assert frm == cmd.candidateId
        if self._should_grant_vote(cmd):
            self.outbox.append(
                Message(
                    frm=self.name,
                    to=frm,
                    cmd=VoteGranted()
                )
            )
        else:
            self.outbox.append(
                Message(
                    frm=self.name,
                    to=frm,
                    cmd=VoteDenied(term=self.currentTerm),
                )
            )

    def _should_grant_vote(self, cmd: RequestVote) -> bool:
        if cmd.term < self.currentTerm:
            return False
        if cmd.lastLogTerm < self.log.last_log_term:
            return False
        if cmd.lastLogIndex < self.log.lastLogIndex:
            return False
        if self.votedFor and self.votedFor != cmd.candidateId:
            return False
        return True


    def _handle_AppendEntries(self, frm: str, cmd: AppendEntries) -> None:
        # TODO: this log.check_log() is rough.
        #       lets convert to appendentries taking a list.
        if not self.log.check_log(cmd.prevLogIndex, cmd.prevLogTerm):
            self.outbox.append(
                Message(
                    frm=self.name,
                    to=frm,
                    cmd=AppendEntriesFailed(term=self.currentTerm),
                )
            )
            return
        self._reset_election_timeout()
        matchIndex = cmd.prevLogIndex
        for entry in cmd.entries:
            assert self.log.add_entry(
                entry, cmd.prevLogIndex, cmd.prevLogTerm, cmd.leaderCommit
            )
            matchIndex += 1
        self.outbox.append(
            Message(
                frm=self.name,
                to=frm,
                cmd=AppendEntriesSucceeded(matchIndex=matchIndex),
            )
        )

    def _become_candidate(self) -> None:
        print(f'** {self.name} is becoming Candidate **')
        self.__class__ = Candidate
        self._call_election()  # pylint: disable=no-member



class Candidate(Server):

    def clock_tick(self, now: float) -> None:
        self.now = now

    def _handle_message(self, msg: Message) -> None:
        if isinstance(msg.cmd, VoteGranted):
            self._votes.add(msg.frm)
            if len(self._votes) > len(self.peers) / 2:
                self._become_leader()

    def _call_election(self):
        self.currentTerm += 1
        self.votedFor = self.name
        self._votes = set([self.votedFor])
        self.outbox.extend(
            Message(frm=self.name, to=p, cmd=RequestVote(
                term=self.currentTerm,
                candidateId=self.name,
                lastLogIndex=self.log.lastLogIndex,
                lastLogTerm=self.log.last_log_term,
            ))
            for p in self.peers if p != self.name
        )

    def _become_leader(self) -> None:
        print(f'** {self.name} is becoming Leader **')
        self.__class__ = Leader
        self._setup_follower_tracking_indexes()
