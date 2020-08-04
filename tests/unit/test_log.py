from raft.log import InMemoryLog, Entry, Command

def test_add_entry_happy_path():
    old_entry = Entry(term=1, committed=False, command=Command('foo', '1'))
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, committed=False, command=Command('foo', '2'))
    log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=1, leaderCommit=0)
    assert log.read()[-1] == new_entry
