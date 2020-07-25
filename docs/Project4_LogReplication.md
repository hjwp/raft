# Project 4 - Log Replication

In Project 3, you created an object `RaftLog` that implemented the Raft transaction log *on a single server*.  Your task in this project is to make a replicated version of the log by introducing networking. To do this, you are going to use the `RaftNetwork` object you created in Project 2.   It is really critical to make sure both of those projects are working before starting this.

This part of the project should not involve a huge amount of code, but you must integrate a number of pieces together to make it work. And it involves even more concurrency.  Also, testing and debugging suddenly become substantially much more difficult. Take it slow. 

## The Scenario

The goal for this project is to make one server (designated in advance as the "leader") replicate its log on all of the other servers. It will do this by sending messages through the network and processing their replies.  You will be able to append new log entries onto the leader log and those entries will just "magically" appear on all of the followers. The leader will be able to bring any follower up to date if its log is missing many entries. Also, the leader will be able to determine consensus.  

## Some Wishful Thinking

Challenge: How do we structure what we need here?   One way to break the analysis paralysis is to engage in a bit of "wishful thinking."  We know that we need a server with both a log and a network connection.  So, wish it into existence:

```
class RaftServer:
    def __init__(self, log, net):
        self.log = log
        self.net = net

# Example setup.
log = RaftLog()
net = RaftNetwork(0)       # Server for node 0
server = RaftServer(log, net)
```

There needs to be a way for the leader to add new entries to its log.  So, define a method on the class to do it. In this method, you add the entries to the local log and then broadcast the new entries to all of the other servers.

```
class RaftServer:
    ...
    def leader_append_entries(self, index, prev_term, entries):
        # Do the operation on the local log
        success = self.log.append_entries(index, prev_term, entries)
        if success:
               # Send an AppendEntries() message to all of the followers
               for follower in followers:
                   self.net.send(follower, AppendEntriesMessage(...))
    ...
```

You know that the followers need to receive this message and respond.  So, add a few methods for dealing with that.  Each of these methods operate on a received message of some kind:

```
class RaftServer:
    ...
    def follower_append_entries(self, msg):
        # Process an AppendEntries messages sent by the leader
        success = self.log.append_entries(msg.index, msg.prev_term, msg.entries)
        self.net.send(msg.source, AppendEntriesResponse(success))
    
    def leader_append_entries_response(self, msg):
        # Process an AppendEntriesResponse message sent by a follower
        if msg.success:
             # AppendEntries on msg.source worked!
             ...
        else:
             # AppendEntries on msg.source failed!
```

Again, we're mainly sketching out the shell of what is actually required to replicate a log.

## Fleshing out Details

Once you've got the shell of what's needed, start to work out more details.  For example, how are messages received?  How are the different methods such as `follower_append_entries()` and `leader_append_entries_response()` actually triggered?

Once you've got basic communication worked out, think about how to handle failed `AppendEntries` messages. Failures occur when the log has gaps/holes or is inconsistent in some way.  To fix this, the leader needs to start working backwards by trying `AppendEntries` operations with lower indices.  You'll need to add some book-keeping for this.   Also, testing it is challenging.

A final step is to add code that determines which entries in the leader's log can be committed because they have been replicated on a quorum of servers.  This involves a bit more book-keeping. 

## Comments

Getting log replication to work might be one of the most difficult parts of the entire Raft project.  It's not necessarily a lot of code, but it integrates everything that you've been working on so far.  Testing and debugging is extremely challenging because you've suddenly got multiple servers running and it's hard to wrap your brain around everything that's happening.   This is where any kind of logging or debugging features in your earlier work will come in useful.

You will likely feel that you are at some kind of impasse where everything is broken or hacked together in some horrible way that should just be thrown out and rewritten.   This is normal.   Expect that certain parts might need to be refactored or improved later.

  

 

