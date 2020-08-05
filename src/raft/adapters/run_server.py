import time
from raft.adapters.network import RaftNetwork, RaftTCPNetwork
from raft.server import Server
from raft.log import InMemoryLog

def run_server(name: str):
    log = InMemoryLog([])  # load from persistent storage at some point
    raftnet = RaftTCPNetwork()  #  may need some info about ports, tbc
    server = Server(name, log=log, currentTerm=0, votedFor=None)
    while True:
        clock_tick(server, raftnet, time.time())
        time.sleep(0.01)

def clock_tick(server: Server, raftnet: RaftNetwork, now: float):
    server.clock_tick(now=now)  # am expecting this to handle timeouts, heartbeats, etc

    for m in raftnet.get_messages(server.name):
        server.handle_message(m)

    while server.outbox:
        m = server.outbox.pop(0)
        raftnet.dispatch(m)
