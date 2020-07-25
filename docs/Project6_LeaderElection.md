# Project 6 - Raft Leader Election

In this project, we work to implement the Raft leader election and state machine for servers switching between follower/candidate/leader roles.  

There are a number of rules that are useful to understand for this project.   However, some of them are rather subtle.  Paper references will be given as appropriate.

1. Time is subdivided into "terms" which are represented by monotonically increasing integers.  There is only one leader per term.

2. The leader sends an AppendEntries message to all followers on a periodic heartbeat timer.  This happens continuously, even if the number of entries being appended is empty (see section 5.2). 

3. All followers await the AppendEntries message on a slightly randomized timeout.  If not received, a follower will call for a new leader election--nominating itself as the candidate (see section 5.2).

4. A server may only vote for a single candidate in a given term.

5. A server only grants a vote to a candidate if the candidate's log is at least as up-to-date as itself. Read section 5.4.1 carefully.  Then read it again.

6. A newly elected leader may NEVER commit entries from a previous entry before it has committed new entries from its own term.   See Figure 8 and section 5.4.2. 

7. All messages in Raft embed the term number of the sender.   If a message with a newer term is received, the receiver immediately becomes a follower.   If a message with an older term is received, a server can ignore the message (or respond with a fail/false status response).  

8. Edge case:  A server that is a candidate should switch to a follower if it receives an AppendEntries message from a server with the same term number as its own.   This can happen if two servers decided to become a candidate at the same time, but one of the servers was successful in getting a majority of votes.   

## Implementation Challenges

One challenge here is implementing the state machine logic in a manner that's isolated enough for testing and debugging.  Can you keep the logic reasonably well isolated from the reset of the server code that needs to send/receive messages, manage timers, and deal with other aspects of the runtime environment?
