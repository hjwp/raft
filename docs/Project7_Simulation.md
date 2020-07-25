# Project 7 - State Machine Simulation

One question about a project like Raft concerns the issue of proving that it's correct.  The overall state space is gigantic.  How do you know that there isn't some obscure corner case that has been overlooked.

One strategy for addressing this problem is to write some kind of state-machine simulation of the system.  We're not going to do that for Raft, but can you write a simulation for the traffic light problem?

## A Mathematical Foundation

Consider the traffic light problem.  Suppose that the state of the system is stored in a Python dictionary like this:

```
init = {
    'name' : 'G1',
    'clock' : 0,
    'out1' : 'G',
    'out2' : 'R',
    'button' : False,
}
```

Here the `name` field is the state name. `clock` is the value of the internal clock.  `out1` and `out2` are the outputs of the light.  `button` is whether or not the pedestrian button has been pressed.

The traffic light has certain operational rules:

1.  The East-West light (out1) stays green for 30 seconds.
2.  The North-South light (out2) stays green for 60 seconds. 
3.  Yellow lights always last 5 seconds.
4.  The push-button causes the North-South light to change immediately if it has been green for more than 30 seconds.  If less than 30 seconds have elapsed, the light will change once it has been green for 30 seconds.

Encode these rules into a single function called `next_state()`.  As input, this function should accept a state dictionary and an event. It should return the next state as a new object. For example:

```
def next_state(state, event):
    ...
    return new_state
```

Here's what it might look like to use the function:

```
>>> next_state(init, "clock")
{'name': 'G1', 'clock': 1, 'out1': 'G', 'out2': 'R', 'button': False }
>>> next_state(_, "clock")
{'name': 'G1', 'clock': 2, 'out1': 'G', 'out2': 'R', 'button': False }
>>> next_state(_, "clock")
{'name': 'G1', 'clock': 2, 'out1': 'G', 'out2': 'R', 'button': False }
>>>
```

What happens if you do this?

```
>>> state = init
>>> while True:
...      print(state)
...      state = next_state(state, "clock")
...
```

## Writing a State Machine Simulator

Using the `next_state()` function, can you write an exhaustive simulation of every possible operational state of the traffic light system?

To do this, you start at the initial state.  You then simulate every possible event that could occur (i.e., clock tick, button press) to get a new set of states.  You then repeat this process for each of those states to get new states.  You keep repeating this process to get more and more states.  Think of it as implementing an exhaustive search of the state space.  If you were playing a game of chess, it's like exploring every possible game configuration that you could reach from a starting point.

In implementing your simulation, you need to keep track of the states that you've already encountered.  Each state should only be processed once. If you don't do this, the simulation could get stuck in an infinite loop as it repeatedly checks states that have already been checked.   Hint: use a set or a dict to track previous states.

## State Machine Safety

In writing such a simulator, what are you actually looking for?   For one, a simulation could act as a kind of giant unit test that executes every possible configuration of the system--if there were fatal flaws in your state machine implementation, they'd be found.  

A simulation could also identify deadlock.   Deadlock is a condition where the `next_state()` function is unable to return a new state--meaning that you're simply stuck. For example, with a traffic light, reaching deadlock might mean the light just freezes in some configuration and never changes ever again.  

You could also use a simulator to verify certain invariants or safety conditions.  For example, suppose you wanted to ensure that the `out1` and `out2` values were not both green at the same time.  This could be implemented as an assertion:

```
assert not (state['out1'] == 'G' and state['out2'] == 'G')
```

Since the simulation runs through every possible state, you'd quickly find out if that assertion was violated in some manner.

## Thoughts for Pondering

How difficulty would it be to write a state machine simulation of Raft?  If you could do it, would a simulation reveal subtle corner cases such new leaders not being allowed to commit entries from previous terms (section 5.4.2 of the Raft paper)?   

Note:  I'm not asking you to simulate Raft (although it could be an interesting challenge if you're up for it).  Actually, a more interesting question might be one of design---could you design the Raft state machine implementation in a manner that would allow it to be simulated?
