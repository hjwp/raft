import json
from typing import List, Protocol
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Entry:
    term: int
    command: str


class Log(Protocol):

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
        leaderCommit: int,  # 1-based, ignored for now
    ) -> bool:
        if not self.check_log(prevLogIndex, prevLogTerm):
            return False
        self._replace_at(prevLogIndex + 1, entry)
        return True


    def read(self) -> List[Entry]:
        return self._log


class PersistentLog:

    def __init__(self, path: Path):
        self.path = path
        if not self.path.exists():
            existing_entries = []
        else:
            existing_entries = [
                Entry(**entry) for entry in json.loads(self.path.read_text())
            ]
        self.log = InMemoryLog(existing_entries)

    def add_entry(
        self,
        entry: Entry,
        prevLogIndex: int,
        prevLogTerm: int,
        leaderCommit: int,
    ) -> bool:
        result = self.log.add_entry(
            entry, prevLogIndex, prevLogTerm, leaderCommit
        )
        self._flush()
        return result

    def read(self) -> List[Entry]:
        return self.log.read()

    def _flush(self) -> None:
        self.path.write_text(json.dumps([asdict(e) for e in self.read()]))
