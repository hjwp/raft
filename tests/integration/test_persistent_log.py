import os
from pathlib import Path
import tempfile
import pytest
from raft.log import Log, PersistentLog, Entry

@pytest.fixture
def temp_path():
    tf = Path(tempfile.NamedTemporaryFile().name)
    return tf
    tf.remove()



def test_loads_log_from_disk(temp_path):
    log = PersistentLog(temp_path)  # type: Log
    entry1 = Entry(1, 'foo=1')
    entry2 = Entry(2, 'foo=2')
    log.add_entry(entry1, 0, 0, 0)
    log.add_entry(entry2, 1, 1, 0)
    log.flush()

    new_log = PersistentLog(temp_path)
    assert new_log.read() == [entry1, entry2]
