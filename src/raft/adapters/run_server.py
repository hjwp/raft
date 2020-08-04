import time
from raft.adapters.network import RaftNetwork, RaftTCPNetwork
from raft.server import Server
from raft.log import InMemoryLog

def run_server(name: str):
    log = InMemoryLog([])  # load from persistent storage at some point
    raftnet = RaftTCPNetwork()  #  may need some info about ports, tbc
    server = Server(name, log=log, currentTerm=0, votedFor=None)
    while True:
        clock_tick(server, raftnet)
        time.sleep(0.01)

def clock_tick(server: Server, raftnet: RaftNetwork):
    server.clock_tick(now=time.time())  # am expecting this to handle timeouts, heartbeats, etc

    for m in raftnet.get_messages():  # just messages for me (S1)
        server.handle_message(m)
    for m in server.outbox:  # server.outbox will be a list of messages to send out
                             # both clock_tick() and handle_message() can add to it
        raftnet.dispatch(m)
