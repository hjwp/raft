from typing import List
import json
from pathlib import Path
from raft.log import Entry, InMemoryLog
from dataclasses import asdict


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
