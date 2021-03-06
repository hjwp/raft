from dataclasses import dataclass
from typing import List, Union
from raft.log import Entry


@dataclass
class ClientSetCommand:
    guid: str
    cmd: str


@dataclass
class ClientSetSucceeded:
    guid: str


@dataclass
class AppendEntries:
    term: int
    leaderId: str
    prevLogIndex: int
    prevLogTerm: int
    entries: List[Entry]
    leaderCommit: int


@dataclass
class AppendEntriesSucceeded:
    matchIndex: int


@dataclass
class AppendEntriesFailed:
    term: int


@dataclass
class RequestVote:
    term: int
    candidateId: str
    lastLogIndex: int
    lastLogTerm: int


@dataclass
class VoteGranted:
    pass


@dataclass
class VoteDenied:
    term: int


@dataclass
class Message:
    frm: str
    to: str
    cmd: Union[
        ClientSetCommand,
        AppendEntries,
        AppendEntriesSucceeded,
        AppendEntriesFailed,
        RequestVote,
        VoteGranted,
        VoteDenied,
    ]
