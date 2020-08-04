from typing import List
from dataclasses import dataclass

@dataclass
class Command:
    key: str
    val: str


@dataclass
class Entry:
    term: int
    committed: bool
    command: Command


class InMemoryLog:

    def __init__(self, log: List[Entry]):
        self._log = log

    def add_entry(
        self,
        entry: Command,
        prevLogIndex: int,
        prevLogTerm: int,
        leaderCommit: int
    ):
        ...

    def read(self):
        return self._log
