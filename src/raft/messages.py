from dataclasses import dataclass
from typing import List, Union, Optional
from raft.log import Entry


@dataclass
class ClientSetCommand:
    cmd: str


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
class Message:
    frm: str
    to: str
    cmd: Union[
        ClientSetCommand, AppendEntries, AppendEntriesSucceeded, AppendEntriesFailed,
    ]
