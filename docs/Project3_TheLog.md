# Project 3 - The Log

The most important part of Raft is the transaction log.  In fact, the whole point of the algorithm is to implement a distributed replicated transaction log!   Everything is ultimately about the log.

In this project, you are going to implement the log as a completely stand-alone object.  This object will have no dependencies on the network, the system, or any other part of Raft.   The primary reason for doing this is testing.  It is absolutely essential that the log gets implemented correctly.  If there are any bugs in it, you will be chasing them through the 9th inner circle of debugging hell if you're trying to figure out what's wrong when it's combined with all of the networking and concurrency code later.

## Background Reading

The behavior of the log is described in section 5.3 and 5.4 of the [Raft Paper](https://raft.github.io/raft.pdf). At first read, it's not going to entirely make sense, but give it a read anyways.  Then proceed.

## The Project

In a nutshell, we're going to make a class `RaftLog` that implements the transaction log.   This class is going to have one primary method on it called `append_entries()`.   Here is the API:

```
class LogEntry:
    def __init__(self, term, item):
        self.term = term
        self.item = item

class RaftLog:
    def append_entries(self, index, prev_term, entries):
        ...
        return success         # success is True/False

    # Additional useful methods
    def __len__(self):
        # Length of the log
        ...

    def __getitem__(self, index):
        # Return log[index]
        ...
```

The `append_entries()` method adds one or more entries to the log and returns a True/False value to indicate success.  The `index` argument specifies the exact position in the log where the entries go.  The `prev_term` argument specifies the `term` value of the log entry immediately before the new entries that are being added.
`entries` is a list of `LogEntry` instances that are being added.

There are a number of very tricky edge cases in the log implementation that need to be accounted for:

1. The log is never allowed to have holes in it.  For example, if there are currently 5 entries in the log, and `append_entries()` tries to add new data at index 9, then the operation fails (return `False`).

2. There is a log-continuity condition where every append operation must also take the term number of the previous entry. For example, if appending at index 9, the `prev_term` value must match the value of `log[8].term`. If there is a mismatch, the operation fails (return `False`).

3. Special case: Appending log entries at index 0 always works. That's the start of the log and there are no prior entries.

4. `append_entries()` is "idempotent."   Basically, that means that `append_entries()` can be called repeatedly with the same arguments and the end result is always the same.  For example, if you called `append_entries()` twice in a row to add the same entry at index 10, it just puts the entry at index 10 and does not result in any data duplication or corruption.

5. Calling `append_entries()` with an empty list of entries is allowed.  In this case, it should report `True` or `False` to indicate if it would have been legal to add new entries at the specified position. 
 
6. If there are already existing entries at the specified log position and all of the conditions for successfully adding a log entry are met (see point 2), the existing entries and everything that follows are deleted.  The new entries are then added in their place. 

## Testing

Of particular interest to this project is Figure 7 of the [Raft Paper](https://raft.github.io/raft.pdf).  You should try to convert Figure 7 to a set of unit tests.  For each these tests, you are performing the following operation on different logs (a-f):

```
# Append entry from term=8 at position 11, prev_term=6 
log.append_entries(11, 6, [ LogEntry(8, "x") ])
```

The result of doing this for Figure 7 is as follows:

(a) False. Missing entry at index 10.
(b) False. Many missing entries.
(c) True. Entry already in position 11 is replaced.
(d) True. Entries at position 11,12 are replaced.
(e) False. Missing entries.
(f) False. Previous term mismatch.

## Persistence

Technically, the Raft log is supposed to be preserved on non-volatile storage and survive a server crash.  How would you modify the `RaftLog` class to support this given that you don't really know how persistence might be implemented just yet?   Note:  I'm not asking you to implement persistence here.   However, it's something you would want to plan for. 




