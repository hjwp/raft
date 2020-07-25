# Exercise : The Stateful Object

A major part of implementing Raft concerns the management of "stateful objects".  That is, an object that behaves in different ways according to some kind of internal operational state.   Here is an example involving a network connection:

```
from socket import socket, AF_INET, SOCK_STREAM

class ConnectionError(Exception):
    pass

class Connection:
    def __init__(self, host, port):
        self.state = 'CLOSED'
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        if self.state != 'CLOSED':
            raise ConnectionError("Not closed")
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.state = 'OPEN'

    def send(self, msg):
        if self.state != 'OPEN':
            raise ConnectionError("Not open")
        return self.sock.send(msg)

    def recv(self, maxbytes):
        if self.state != 'OPEN':
            raise ConnectionError("Not open")
        return self.sock.recv(maxbytes)

    def close(self):
        if self.state != 'OPEN':
            raise ConnectionError("Not open")
        self.sock.close()
        self.state = 'CLOSED'
```

In this code, the `Connection` object has an internal variable that indicates its state. Different methods alter their behavior based on the state (signaling an error versus succeeding for instance). 

## Can you do better?

From a coding a perspective, the `Connection` class has already become a bit messy even with just two operational states.  What if there were even more states?    Would it turn into a giant mess of if-statements?

Your challenge:  Think about how you might reimplement the above `Connection` class.  For example, can you refactor the code to operate in the same way, but with no if-statements at all?
