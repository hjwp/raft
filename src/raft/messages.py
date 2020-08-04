from dataclasses import dataclass
from typing import List, Union
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
class AppendEntriesResponse:
    frm: str
    term: int
    success: bool


@dataclass
class Message:
    frm: str
    to: str
    cmd: Union[ClientSetCommand, AppendEntries, AppendEntriesResponse]
