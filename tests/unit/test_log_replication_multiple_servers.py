from typing import List
from raft.adapters.run_server import clock_tick
from raft.log import InMemoryLog
from raft.messages import Message, ClientSetCommand
from raft.server import Leader, Follower

class FakeRaftNetwork:
    def __init__(self, me: str, messages: List[Message]):
        self.me = me
        self.messages = messages

    def get_messages(self) -> List[Message]:
        """retrieve my messages, and take them out of the network"""
        mine = [m for m in self.messages if m.to == self.me]
        for m in mine:
            self.messages.remove(m)
        return mine

    def dispatch(self, msg: Message) -> None:
        """put the message into the network"""
        self.messages.append(msg)


def test_replication_one_server():
    peers = ["S2"]

    leader_log = InMemoryLog([])
    leader = Leader(
        name="S1", peers=peers, log=leader_log, currentTerm=1, votedFor=None
    )

    follower_log = InMemoryLog([])
    follower = Follower(name="S2", log=follower_log, currentTerm=1, votedFor=None)

    client_set = Message(frm='client.id', to='S1', cmd=ClientSetCommand('foo=1'))

    messages = []  # type: List[Message]
    lnet = FakeRaftNetwork(me="S1", messages=messages)
    fnet = FakeRaftNetwork(me="S2", messages=messages)
    messages.append(client_set)
    clock_tick(leader, lnet)
    clock_tick(follower, fnet)
    assert follower.log.read()[-1].cmd == client_set.cmd.cmd

def test_replication_multiple_servers():
    peers = ("S2", "S3")

    leader_log = InMemoryLog([])
    leader = Leader(
        name="S1", peers=peers, log=leader_log, currentTerm=1, votedFor=None
    )

    f1_log = InMemoryLog([])
    f1 = Follower(name="S2", log=f1_log, currentTerm=1, votedFor=None)
    f2_log = InMemoryLog([])
    f2 = Follower(name="S3", log=f1_log, currentTerm=1, votedFor=None)

    client_set = Message(frm='client.id', to='S1', cmd=ClientSetCommand('foo=1'))

    messages = []  # type: List[Message]
    lnet = FakeRaftNetwork(me="S1", messages=messages)
    f1net = FakeRaftNetwork(me="S2", messages=messages)
    f2net = FakeRaftNetwork(me="S3", messages=messages)
    messages.append(client_set)
    clock_tick(leader, lnet)
    clock_tick(f1, f1net)
    clock_tick(f2, f2net)
    assert f1.log.read()[-1].cmd == client_set.cmd.cmd
    assert f2.log.read()[-1].cmd == client_set.cmd.cmd
