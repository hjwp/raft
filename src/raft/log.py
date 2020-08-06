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

    def entry_term(self, index: int) -> int:
        """term of entry at (1-based) index position"""
        ...

    def entry_at(self, index: int) -> Entry:
        """Entry at (1-based) index position"""
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

    def _replace_at(self, index: int, entry: Entry) -> None:
        """1-based index. truncates any after, unless entry matches"""
        if self._has_entry_at(index) and self.entry_at(index) == entry:
            return
        self._log = self._log[:index - 1] + [entry]

    @property
    def lastLogIndex(self) -> int:
        return len(self._log)

    @property
    def last_log_term(self) -> int:
        if len(self._log) == 0:
            return 0
        return self.entry_term(self.lastLogIndex)

    def entry_term(self, index: int) -> int:
        if index == 0:
            return 0
        return self.entry_at(index).term

    def entry_at(self, index: int) -> Entry:
        if index < 0:
            return self._log[index]
        return self._log[index - 1]

    def check_log(self, prevLogIndex: int, prevLogTerm: int) -> bool:
        """check whether prevLogIndex and prevLogTerm match.  1-based index"""
        if prevLogIndex == 0:
            return True
        if not self._has_entry_at(prevLogIndex):
            print(f'nope, no entry at {prevLogIndex}')
            return False
        if self.entry_term(prevLogIndex) != prevLogTerm:
            print(f'nope, entry at {prevLogIndex} had wrong term')
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
