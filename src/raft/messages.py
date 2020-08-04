from dataclasses import dataclass
from typing import List, Union
from raft.log import Entry

@dataclass
class AppendEntries:
    term: int
    leaderId: str
    prevLogIndex: int
    prevLogTerm: int
    entries: List[Entry]
    leaderCommit: int


@dataclass
class Message:
    to: str
    cmd: Union[AppendEntries]
