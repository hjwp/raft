# pylint: disable=redefined-outer-name
import sys
import time
from typing import Tuple
from raft.log import InMemoryLog
from raft.adapters.network import RaftNetwork, TCPRaftNet
from raft.server import Server, Follower

def run_tcp_server(server: Server, raftnet: RaftNetwork):
    print(f'Starting server {server.name}')
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


def _main(name: str) -> Tuple[Server, RaftNetwork]:
    # pylint: disable=import-outside-toplevel
    raftnet = TCPRaftNet(name)
    raftnet.start()
    server = Follower(
        name=name, log=InMemoryLog([]), now=time.time(), currentTerm=0, votedFor=None
    )
    import threading
    threading.Thread(target=run_tcp_server, args=(server, raftnet), daemon=True).start()
    return server, raftnet

if __name__ == '__main__':
    server, raftnet = _main(sys.argv[1])
