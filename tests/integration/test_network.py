import socket
import time
from raft.adapters.network import TCPRaftNet
from raft.messages import Message, AppendEntriesSucceeded
from raft.adapters.transport import connect_tenaciously

def test_sending_message():
    s1net = TCPRaftNet('S1')
    s2net = TCPRaftNet('S2')
    s1net.start()
    s2net.start()

    # check servers are up and listening
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        host, port = s1net.host
        connect_tenaciously(sock, host=host, port=port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        host, port = s2net.host
        connect_tenaciously(sock, host=host, port=port)

    msg = Message(frm='S1', to='S2', cmd=AppendEntriesSucceeded(3))
    s1net.dispatch(msg)
    time.sleep(0.2)
    msgs = s2net.get_messages('S2')
    assert msgs == [msg]
