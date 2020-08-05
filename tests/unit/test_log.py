from raft.log import InMemoryLog, Entry

def test_some_helpers():
    entries = [
        Entry(term=1, cmd="foo=1"),
        Entry(term=2, cmd="foo=2"),
        Entry(term=3, cmd="foo=3"),
    ]
    log = InMemoryLog(entries)
    assert log.lastLogIndex == 3
    assert log.entry_term(1) == 1
    assert log.entry_term(2) == 2
    assert log.entry_term(3) == 3
    assert log.entry_term(0) == 0
    assert log.entry_term(-1) == 3

    assert log.entry_at(1) == entries[0]
    assert log.entry_at(2) == entries[1]
    assert log.entry_at(3) == entries[2]
    assert log.entry_at(-1) == entries[2]



def test_add_entry_happy_path():
    old_entry = Entry(term=1, cmd="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=2, cmd="foo=2")
    result = log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=1, leaderCommit=0)
    assert log.read()[-1] == new_entry
    assert result is True


def test_add_first_entry():
    log = InMemoryLog([])
    new_entry = Entry(term=1, cmd="foo=2")
    log.add_entry(new_entry, prevLogIndex=0, prevLogTerm=0, leaderCommit=0)
    assert log.read() == [new_entry]


def test_idempotent_at_end():
    old_entry = Entry(term=1, cmd="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, cmd="foo=2")
    log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=1, leaderCommit=0)
    result = log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=1, leaderCommit=0)
    assert log.read() == [old_entry, new_entry]
    assert result is True


def test_cannot_add_past_end():
    old_entry = Entry(term=1, cmd="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, cmd="foo=2")
    result = log.add_entry(new_entry, prevLogIndex=2, prevLogTerm=1, leaderCommit=0)
    assert log.read() == [old_entry]
    assert result is False


def test_cannot_add_if_prevLogTerm_does_not_Match():
    old_entry = Entry(term=1, cmd="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, cmd="foo=2")
    result = log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=2, leaderCommit=0)
    assert log.read() == [old_entry]
    assert result is False


def test_cannot_add_if_prevLogTerm_does_not_match():
    old_entry = Entry(term=1, cmd="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, cmd="foo=2")
    result = log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=2, leaderCommit=0)
    assert log.read() == [old_entry]
    assert result is False


def test_can_overwrite_one_if_prevLogTerm_matches():
    old_log = [Entry(term=1, cmd="foo=1"), Entry(term=1, cmd="foo=2")]
    log = InMemoryLog(old_log)
    new_entry = Entry(term=2, cmd="foo=3")
    result = log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=1, leaderCommit=0)
    assert log.read() == [old_log[0], new_entry]
    assert result is True


def test_edge_case_can_ovewrite_zeroth_entry_if_its_the_only_one():
    old_entry = Entry(term=1, cmd="foo=1")
    log = InMemoryLog([old_entry])
    new_entry = Entry(term=1, cmd="foo=2")
    result = log.add_entry(new_entry, prevLogIndex=0, prevLogTerm=0, leaderCommit=0)
    assert log.read() == [new_entry]
    assert result is True


def test_edge_case_can_ovewrite_zeroth_entry_and_all_following():
    old_log = [
        Entry(term=1, cmd="foo=1"),
        Entry(term=1, cmd="foo=2"),
        Entry(term=1, cmd="foo=3"),
    ]
    log = InMemoryLog(old_log)
    new_entry = Entry(term=2, cmd="bar=1")
    result = log.add_entry(new_entry, prevLogIndex=0, prevLogTerm=0, leaderCommit=0)
    assert log.read() == [new_entry]
    assert result is True


def test_valid_overwrite_in_the_middle_of_the_log_kills_all_later_ones():
    old_log = [
        Entry(term=1, cmd="foo=1"),
        Entry(term=1, cmd="foo=2"),
        Entry(term=1, cmd="foo=3"),
    ]
    log = InMemoryLog(old_log)
    new_entry = Entry(term=2, cmd="bar=1")
    result = log.add_entry(new_entry, prevLogIndex=1, prevLogTerm=1, leaderCommit=0)
    assert log.read() == [old_log[0], new_entry]
    assert result is True



def test_check_log_happy_path():
    old_entry = Entry(term=1, cmd="foo=1")
    log = InMemoryLog([old_entry])
    result = log.check_log(prevLogIndex=1, prevLogTerm=1)
    assert result is True


def test_check_log_when_empty():
    log = InMemoryLog([])
    result = log.check_log(prevLogIndex=0, prevLogTerm=0)
    assert result is True

def test_prevLogIndex_zero_is_always_true():
    log = InMemoryLog([Entry(term=1, cmd='foo=1')])
    result = log.check_log(prevLogIndex=0, prevLogTerm=0)
    assert result is True


def test_check_log_index_past_end():
    old_entry = Entry(term=1, cmd="foo=1")
    log = InMemoryLog([old_entry])
    result = log.check_log(prevLogIndex=2, prevLogTerm=1)
    assert result is False


def test_prevLogTerm_does_not_Match():
    old_entry = Entry(term=1, cmd="foo=1")
    log = InMemoryLog([old_entry])
    result = log.check_log(prevLogIndex=1, prevLogTerm=2)
    assert result is False
