import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from raft.log import Entry, InMemoryLog


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

    @property
    def lastLogIndex(self) -> int:
        return self.log.lastLogIndex

    @property
    def last_log_term(self) -> int:
        return self.log.last_log_term

    def check_log(self, prevLogIndex: int, prevLogTerm: int) -> bool:
        return self.log.check_log(prevLogIndex, prevLogTerm)

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
