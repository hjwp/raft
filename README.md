# Rafting Trip - August 3-7, 2020

Hello! This is the course project repo for the "Rafting Trip"
course.  This project will serve as the central point of discussion, code
sharing, debugging, and other matters related to the project.

Although each person will work on their own code, it is requested
that all participants work from this central repo. First, create a
a branch for yourself:

    bash % git clone https://github.com/dabeaz-course/raft_2020_08
    bash % cd raft_2020_08
    bash % git checkout -b yourname
    bash % git push -u origin yourname

Do all of your subsequent work in your branch of this central repository. 

The use of GitHub makes it easier for me to look at your code and
answer questions (you can point me at your code, raise an issue,
etc.).  It also makes it easier for everyone else to look at your code
and to get ideas.  Implementing Raft is hard. Everyone is going to
have different ideas about the implementation, testing, and other
matters.  By having all of the code in one place, it will be better
and more of a shared experience.

I will also be using the repo to commit materials, solutions, and 
other things as the course date nears and during the course itself.

Finally, the repo serves as a good record for everything that happened
during the course after the fact.  

Cheers,
Dave

## Live Session

The course is conducted live from 09:30 to 17:30 US Central Time
(UTC-05:00) on Zoom.  I will be there about 30 minutes ahead of time
if you need to test your set up.  Here are meeting details:

* Topic: Rafting Trip, June 1-5, 2020
* Time: 9:30am - 5:30pm US CDT (UTC-05:00)
* Join Zoom Meeting https://us02web.zoom.us/j/81316240543?pwd=MWdNTll6N3dKZkdTcmJrTEFvdXRVZz09
* Meeting ID: 813 1624 0543
* Password: 817350

## Live Chat

For live chat during the course, we use Gitter.  Here is a link:

* [https://gitter.im/dabeaz-course/raft_2020_08](https://gitter.im/dabeaz-course/raft_2020_08)

## Raft Resources

Our primary source of information on Raft is found at https://raft.github.io.
You should also watch the video at https://www.youtube.com/watch?v=YbZ3zDzDnrw

## The Challenge of Raft

One of the biggest challenges in the Raft project is knowing precisely
where to start.  As you read the Raft paper, you should be thinking
about "where would I actually start with an implementation?"  There
are different facets that need to be addressed.  For example, at one
level, there's a networking layer involving machines and
messages. Maybe this is the starting point (at the low level).
However, there's also the "logic" of Raft, encoded as a state machine
(Leader, Follower, Candidate).  So, an alternative might be to
approach from a high level instead.  And then there are applications
that might utilize Raft such as a key-value store database. Do you
build that first and then expand Raft on top of it?

The other challenge concerns testing and debugging.  How do you
implement it while having something that you can actually test and
verify?

## Introductory Video

* [Course Setup](https://vimeo.com/401115908/a81c795591) (2 mins)
* [Course Introduction and Background](https://vimeo.com/401856540/3e8cf8b01a) (20 min)

## Live Session Videos

Videos from the live course discussion will appear here.

## Preparation Exercises

The following material might help you prepare for the course.

* [Socket Exercise](docs/SocketWarmup.md)
* [Key-Value Store](docs/Key-Value-Store.md)
* [Stateful Object](docs/StatefulObjects.md)

The Raft project is similar to what might be taught in a graduate
distributed systems course such as MIT 6.824. A lot of information is
available on the course
[website](https://pdos.csail.mit.edu/6.824/index.html).

## State Machine Exercise

A core part of Raft concerns the implementation of state machines.
The following exercise will be discussed in some detail.  You are
encouraged to work on it in advance and to think about it:

* [The Traffic Light](docs/The-Traffic-Light.md)

## Project Milestones

The following projects guide you through one possible path for implementing Raft.
This is not necessarily the only way to do it.  However, it's an approach
that has often worked in the past.

* [Project 1 - Message Passing](docs/Project1_Messaging.md)
* [Project 2 - Raft Network](docs/Project2_RaftNet.md)
* [Project 3 - The Log](docs/Project3_TheLog.md)
* [Project 4 - Log Replication](docs/Project4_LogReplication.md)
* [Project 5 - State Machines](docs/Project5_StateMachines.md)
* [Project 6 - Raft Leader Election](docs/Project6_LeaderElection.md)
* [Project 7 - State Machine Simulation](docs/Project7_Simulation.md)
* [Project 8 - Raft Client/Key Value Store](docs/Project8_RaftClient.md)

## Interesting Resources

* [Concurrency: the Works of Leslie Lamport](docs/documents/3335772.pdf) (PDF)
* [Implementing Raft, Eli Bendersky](https://eli.thegreenplace.net/2020/implementing-raft-part-0-introduction/) (blog)


