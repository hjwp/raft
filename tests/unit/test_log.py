from raft.log import InMemoryLog, Entry


def test_add_entry_happy_path():
    old_entry = Entry(term=1, command="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, command="foo=2")
    result = log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=1, leaderCommit=0)
    assert log.read()[-1] == new_entry
    assert result is True


def test_add_first_entry():
    log = InMemoryLog([])
    new_entry = Entry(term=1, command="foo=2")
    log.add_entry(new_entry, prevLogIndex=0, prevLogTerm=0, leaderCommit=0)
    assert log.read() == [new_entry]


def test_idempotent_at_end():
    old_entry = Entry(term=1, command="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, command="foo=2")
    log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=1, leaderCommit=0)
    result = log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=1, leaderCommit=0)
    assert log.read() == [old_entry, new_entry]
    assert result is True


def test_cannot_add_past_end():
    old_entry = Entry(term=1, command="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, command="foo=2")
    result = log.add_entry(new_entry, prevLogIndex=2, prevLogTerm=1, leaderCommit=0)
    assert log.read() == [old_entry]
    assert result is False


def test_cannot_add_if_prevLogTerm_does_not_Match():
    old_entry = Entry(term=1, command="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, command="foo=2")
    result = log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=2, leaderCommit=0)
    assert log.read() == [old_entry]
    assert result is False

def test_idempotent_at_end():
    old_entry = Entry(term=1, command="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, command="foo=2")
    log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=1, leaderCommit=0)
    result = log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=1, leaderCommit=0)
    assert log.read() == [old_entry, new_entry]
    assert result is True


def test_cannot_add_past_end():
    old_entry = Entry(term=1, command="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, command="foo=2")
    result = log.add_entry(new_entry, prevLogIndex=2, prevLogTerm=1, leaderCommit=0)
    assert log.read() == [old_entry]
    assert result is False


def test_cannot_add_if_prevLogTerm_does_not_match():
    old_entry = Entry(term=1, command="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, command="foo=2")
    result = log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=2, leaderCommit=0)
    assert log.read() == [old_entry]
    assert result is False

