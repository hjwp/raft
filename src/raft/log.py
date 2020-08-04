from typing import List, Protocol
from dataclasses import dataclass


@dataclass
class Entry:
    term: int
    cmd: str


class Log(Protocol):

    @property
    def lastLogIndex(self) -> int:
        """1-based index of latest entry"""
        ...

    @property
    def last_log_term(self) -> int:
        """term of latest entry"""
        ...

    def check_log(self, prevLogIndex: int, prevLogTerm: int) -> bool:
        ...

    def add_entry(
        self,
        entry: Entry,
        prevLogIndex: int,
        prevLogTerm: int,
        leaderCommit: int,
    ) -> bool:
        ...

    def read(self) -> List[Entry]:
        ...


class InMemoryLog:

    def __init__(self, log: List[Entry]) -> None:
        self._log = log

    def _has_entry_at(self, index: int) -> bool:
        """1-based"""
        return 0 < index <= len(self._log)

    def _entry_at(self, index: int) -> Entry:
        """return 1-based index entry"""
        return self._log[index - 1]

    def _replace_at(self, index: int, entry: Entry) -> None:
        """1-based index. truncates any after"""
        self._log = self._log[:index - 1] + [entry]

    @property
    def lastLogIndex(self) -> int:
        return len(self._log)

    @property
    def last_log_term(self) -> int:
        if len(self._log) == 0:
            return 0
        return self._entry_at(self.lastLogIndex).term

    def check_log(self, prevLogIndex: int, prevLogTerm: int):
        """check whether prevLogIndex and prevLogTerm match.  1-based index"""
        if prevLogIndex == 0:
            return True
        if not self._has_entry_at(prevLogIndex):
            return False
        if self._entry_at(prevLogIndex).term != prevLogTerm:
            return False
        return True

    def add_entry(
        self,
        entry: Entry,
        prevLogIndex: int,  # 1-based
        prevLogTerm: int,
        leaderCommit: int,  # 1-based, ignored for now.  # TODO: remove?
    ) -> bool:
        if not self.check_log(prevLogIndex, prevLogTerm):
            return False
        self._replace_at(prevLogIndex + 1, entry)
        return True


    def read(self) -> List[Entry]:
        return self._log
