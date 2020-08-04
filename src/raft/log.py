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
        return 0 < index <= len(self._log)

    def _entry_at(self, index: int) -> Entry:
        """return 1-based index entry"""
        return self._log[index - 1]

    def _replace_entry(self, index: int, entry: Entry) -> None:
        """1-based"""
        assert self._has_entry_at(index)
        self._log[index - 1] = entry

    def _truncate_after(self, index: int) -> None:
        self._log = self._log[:index]

    def add_entry(
        self,
        entry: Entry,
        prevLogIndex: int,  # 1-based
        prevLogTerm: int,
        leaderCommit: int,  # 1-based, ignored for now
    ) -> bool:

        if prevLogIndex == 0:
            if len(self._log) == 0:
                self._log.append(entry)
                return True
            if len(self._log) == 1:
                self._replace_entry(1, entry)
                return True
            return  False

        if not self._has_entry_at(prevLogIndex):
            return False

        prev_entry = self._entry_at(prevLogIndex)
        if prev_entry.term != prevLogTerm:
            return False

        new_index = prevLogIndex + 1
        if self._has_entry_at(new_index):
            self._replace_entry(new_index, entry)
            self._truncate_after(new_index)
            return True

        self._log.append(entry)
        return True


    def read(self) -> List[Entry]:
        return self._log
