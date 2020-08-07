from typing import Dict
from raft.server import Server, Leader, Follower
from raft.log import InMemoryLog, Entry

logs_from_paper_str = '''
    l,1114455666
    a,111445566
    b,1114
    c,11144556666
    d,111445566677
    e,1114444
    f,11122233333
'''

def make_servers() -> Dict[str, Server]:
    servers = {}
    peers = [c for c in 'labcdef']
    for line in logs_from_paper_str.strip().splitlines():
        name, _, entries = line.strip().partition(',')
        log = InMemoryLog([
            Entry(term=int(c), cmd=f'foo={c}')
            for c in entries
        ])
        args = dict(
            name=name, peers=peers, now=0, log=log, currentTerm=int(entries[-1]), votedFor=None
        )
        if name == 'l':
            servers[name] = Leader(**args)
        else:
            servers[name] = Follower(**args)
    return servers
