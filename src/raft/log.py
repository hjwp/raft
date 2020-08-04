from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Entry:
    term: int
    command: str


class InMemoryLog:

    def __init__(self, log: List[Entry]) -> None:
        self._log = log

    @property
    def lastLogIndex(self):
        """1-based"""
        return len(self._log)

    def _has_entry_at(self, index: int) -> bool:
        """1-based"""
        return index <= len(self._log)

    def _entry_at(self, index: int) -> Entry:
        """return 1-based index entry"""
        return self._log[index - 1]

    def add_entry(
        self,
        entry: Entry,
        prevLogIndex: int,  # 1-based
        prevLogTerm: int,
        leaderCommit: int,  # 1-based, ignored for now
    ) -> bool:
        if prevLogIndex > self.lastLogIndex:
            return False
        new_index = prevLogIndex + 1
        if prevLogIndex == 0:
            # TODO: what if it shouldn't be?
            self._log.append(entry)
            return True

        if self._has_entry_at(new_index) and self._entry_at(new_index) == entry:
            return True

        prev_entry = self._entry_at(prevLogIndex)
        if prev_entry.term != prevLogTerm:
            return False

        self._log.append(entry)
        return True


    def read(self) -> List[Entry]:
        return self._log
