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

