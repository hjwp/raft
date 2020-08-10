# Rafting Trip - August 3-7, 2020

This was my code from David Beazley's amazing [Rafting
Trip](https://dabeaz.com/raft.html) training course,
where we tried to implement the
[raft distributed consensus algorithm](https://raft.github.io/)
in a week.

I didn't finish, but I got fairly far.  Code here for my archive.


* [x] transaction log class with accept/reject logic for append requests
* [x] vaguely ports & adapters architecture, with raft protocol classes as core domain
* [x] optional persistent log storage adapter
* [x] log replication leader -> follower, with backtracking algorithm
* [x] heartbeats + time events
* [x] elections, including timeouts, conversion to candidate, voting, promotion to leader
* [x] `RaftNet` abstraction for transport, with fake version for tests
* [x] `run_server()` and `clock_tick()` abstractions for running the algo over time
* [x] ability to unit test / simulate interaction of multiple nodes in-memory
* [x] end-to-end and integration tests
* [ ] client interactions  `<--` this is the big missing piece, which might
      have caused me to rethink the architecture.  may require some intermediary
      piece in between Server objects / `run_server()` and clients.
* [ ] cluster membership changes
