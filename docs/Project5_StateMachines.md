# Project 5 - State Machines

A core part of Raft involves implementing the state machine for leaders, followers, and candidates.  To wrap one's brain around this, it might help to work a slightly simpler example first.  So, we're going to take a diversion and implement the state machine for a traffic light.

Visit the [Traffic Light Exercise](The-Traffic-Light.md)

## New Requirements

You may have solved the traffic light problem as part of course warmup.  However, in this project, see if you can solve in a way where the state machine logic is completely decoupled from any runtime logic involving timers, buttons, or output light modules.   Can you implement the state machine logic as a standalone class that can be tested and used on its own?

We'll largely work through this as a group with some live coding.
