import time
import socket
import pytest
from typing import List
from raft.adapters.run_server import clock_tick
from raft.adapters.network import RaftNetwork, TCPRaftNet
from raft.adapters.transport import connect_tenaciously
from raft.log import InMemoryLog, Entry
from raft.messages import Message, ClientSetCommand
from raft.server import Leader, Follower, Server

def run_tcp_server(server: Server, raftnet: RaftNetwork):
    while True:
        clock_tick(server, raftnet, time.time())
        time.sleep(0.01)

def test_replication_with_tcp_servers():
    networks = {
        name: TCPRaftNet(name) 
        for name in TCPRaftNet.SERVERS
    }
    for net in networks.values():
        net.start()

    # check networks are up and listening
    for net in networks.values():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            host, port = net.host
            connect_tenaciously(sock, host=host, port=port)

    leader_entries = [
        Entry(term=1, cmd="monkeys=1"),
        Entry(term=2, cmd="bananas=2"),
        Entry(term=2, cmd="turtles=3"),
    ]
    one_wrong_entry = [
        Entry(term=1, cmd="monkeys=1"),
        Entry(term=1, cmd="monkeys=2"),
    ]

    leader = Leader(
        name="S1",
        log=InMemoryLog(leader_entries),
        now=1,
        peers=["S2", "S3"],
        currentTerm=2,
        votedFor=None,
    )
    f1 = Follower(name="S2", log=InMemoryLog([]), now=1, currentTerm=2, votedFor=None)
    f2 = Follower(
        name="S3", log=InMemoryLog(one_wrong_entry), now=1, currentTerm=2, votedFor=None
    )

    client_set = Message(frm="client.id", to="S1", cmd=ClientSetCommand("gherkins=4"))

    leadernet = networks['S1']
    f1net = networks['S2']
    f2net = networks['S3']
    randomnet = networks['S5']

    randomnet.dispatch(client_set)

    for i in range(1, 20):
        print(f'*** --- CLOCK TICK {i} --- ***')
        time.sleep(0.2)
        clock_tick(leader, leadernet, i)
        clock_tick(f1, f1net, i)
        clock_tick(f2, f2net, i)

    expected = leader_entries + [Entry(term=2, cmd="gherkins=4")]

    assert leader.log.read() == expected
    assert f1.log.read() == expected
    assert f2.log.read() == expected
