# Project 8 - Raft Client

The final project is simple--just get the rest of Raft working.  Actually, the goal here is to see if you can apply Raft to the key-value store you created earlier.   To do this, you're going to need to work out the basic details concerning the client-leader interaction. 

1.  The Raft algorithm needs some mechanism to "apply the transaction log to the state machine." Basically, this means taking the committed log entries and running them on the key-value store.  For example, if the log records an entry such as `('set', 'foo', 42)`.  Applying the entry means performing the operation on the key-value store.

2. Clients need some way to locate the leader of the Raft cluster.

3. Clients need some kind of timeout/retry mechanism to account for leader crashes or other problems.

If you're up for it, you can also tackle some of the problems address in Section 8 of the Raft paper.
