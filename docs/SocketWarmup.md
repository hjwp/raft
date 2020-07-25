# Introduction to Sockets

A core part of implementing Raft concerns communication between machines in the form of messages.  To do that, we're going to use sockets (or possibly some other low-level equivalent).   This exercise goes through some basics of using sockets and communication with messages.   Python is shown, but sockets are implemented in most other programming languages using a comparable interface.

## Creating a Socket

A socket represents an end-point for communicating on the network.  Think of it as being similar to a file. With a file, you use the `open()` function to create a file object and then you use `read()` and `write()` methods to process data.  A socket is a similar idea.  

To create a socket, use the `socket` library.  For example:

```
from socket import socket, AF_INET, SOCK_STREAM
sock = socket(AF_INET, SOCK_STREAM)
```

The `AF_INET` option specifies that you are using the internet (version 4) and the `SOCK_STREAM` specifies that you want a reliable data stream.  In technical terms, this socket will be used for TCP/IPv4 communication.  Change the `AF_INET` to `AF_INET6` if you want to use TCP/IPv6.

## Making a Connection

Further use of a socket depends on the program's role in the communication.  If a program is going to wait and listen for incoming connections, it is known as a server.  If a program makes an outgoing connection, it is a client.  The client case is simpler so let's start with that.  Here's an example of using a socket to make an outgoing HTTP request and reading the response:

```
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('www.python.org', 80))
sock.send(b'GET /index.html HTTP/1.0\r\n\r\n')
parts = []
while True:
    part = sock.recv(1000)     # Receive up to 1000 bytes (might be less)
    if not part:
        break                  # Connection closed
    parts.append(part)
# Form the complete response
response = b''.join(parts)
print("Response:", response)
```

Try running the above program.   You'll probably get a response indicating some kind of error.  That is fine. Our goal is not to implement HTTP, but simply to see some communication.

Now, a few important details.

1. Network addresses are specified as a tuple `(hostname, port)` where `port` is a number in the range 0-65535.

2. The port number must be known in advance.  This is usually dictated by a standard. For example, port 25 is used for email, port 80 is used for HTTP, and port 443 is used for HTTPS.  See https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml

3. Data is sent using `sock.send()`.  Data is received `sock.recv()`.  Both of these operations only work with byte-strings.  If you are working with text (Unicode), you will need to make sure it's properly encoded/decoded from bytes.

4. Data is received and transmitted in fragments.  The `sock.recv()` accepts a maximum number of bytes, but that it is only a maximum.  The actual number of bytes returned might be much less. It is your responsibility to reassemble data from fragments into a complete response.  Thus, you might have to collect parts and put them back together as shown.   A closed connection or "end of file" is indicated by `sock.recv()` returning an empty byte string.

## Receiving Connections

Receiving connections on a socket is a bit more complicated.  Recall that clients (above) need to know the address and port number in order to make a connection.   To receive a connection, a program first needs to bind a socket to a port.  Here's how you do that:

```
sock = socket(AF_INET, SOCK_STREAM)
sock.bind(('', 12345))         # Bind to port 12345 on this machine
sock.listen(1)                 # Enable incoming connections
```

The magic number `1` provided to `listen()` relates to how many incoming connections can be "in progress" inside the host operating system. That's a complicated topic that's not relevant to the Raft project. However, you still have to give `listen()` a number and it has to be greater than 0.

To accept a connection, use the `sock.accept()` method:

```
client, addr = sock.accept()     # Wait for a connection
```

`accept()` returns two values.  The first is a completely new socket object that represents the connection back to the client.  The second is the remote address `(host, port)` of the client.   You use the `client` socket for further communication.  Use the address `addr` for diagnostics and to do things like reject connections from unknown locations.

One confusion with servers concerns the initial socket that you create (`sock`).   The initial socket really only serves as a connection point for clients. Think of it like the phone operator for a large company.  You call the central number.  The operator asks you who you're trying to reach and then you're connected to a different line.  It's the same general idea here.  All communication will use the `client` socket returned by `sock.accept()`. 

Here is an example of a server that reports the current time back to clients:

```
import time
from socket import socket, AF_INET, SOCK_STREAM

sock = socket(AF_INET, SOCK_STREAM)
sock.bind(('',12345)
sock.listen(1)
while True:
    client, addr = sock.accept()
    print('Connection from', addr)
    msg = time.ctime()    # Get current time
    client.sendall(msg.encode('utf-8'))
    client.close()
```

Try running this program on your machine.  While it is running, try connecting to it from a separate program.

```
from socket import socket, AF_INET, SOCK_STREAM

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('localhost', 12345)
msg = sock.recv(1000)              # Get the time
print('Current time is:', msg.decode('utf-8'))
```

Run this program (separately from the server).  You should see it print the current time.

## Exercise

Modify the time program above to operate as an echo server.  An echo server reads data from the client and simply echos it back.   For example, here's a client that shows the intended behavior:

```
from socket import socket, AF_INET, SOCK_STREAM

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('localhost', 12345)
msg = b'Hello World'
sock.sendall(msg)
response = sock.recv(len(msg))
assert response == msg
```

Now, a test.  Modify the above client to keep increasing the size of the message that's sent. How large can it get before everything fails?  How does it fail? Why does it fail?  

## Message Passing

To make messaging more sane, it is sometimes common to use size-prefixed messages.  This is a technique where every message is prepended with a byte-count to indicate how large the message is.  Here is some sample code that sends a size-prefixed message:

```
def send_message(sock, msg):
    size = b'%10d' % len(msg)    # Make a 10-byte length field
    sock.sendall(size)
    sock.sendall(msg)
```

Write the corresponding `recv_message(sock)` function.  This function should read the size, then read exactly that many bytes to return the exact message that was sent.

When you are done, rewrite your echo server and client to use `send_message()` and `recv_message()`.  Run some tests to see if they work messages of any size.  Also see if your client/server can reliably exchange thousands messages back and forth on the same connection.   Maybe run a test to see how fast it is.



 