# pylint: disable=redefined-outer-name
from pathlib import Path
import tempfile
import pytest
from raft.log import Log
from raft.adapters.persistent_log import PersistentLog, Entry

@pytest.fixture
def temp_path():
    tf = Path(tempfile.NamedTemporaryFile().name)
    yield tf
    tf.unlink()



def test_can_round_trip_a_log(temp_path):
    log = PersistentLog(temp_path)  # type: Log
    entry1 = Entry(1, 'foo=1')
    entry2 = Entry(2, 'foo=2')
    log.add_entry(entry1, 0, 0, 0)
    log.add_entry(entry2, 1, 1, 0)
    new_log = PersistentLog(temp_path)
    assert new_log.read() == [entry1, entry2]
