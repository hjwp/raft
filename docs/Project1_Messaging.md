# Project 1 - Message Transport

Raft involves servers that send messages to each other.   Thus, our first project is to implement two functions that do just that over a network socket:

```
# transport.py

def send_message(sock, msg):
    ...

def recv_message(sock):
    ...
```

A critical feature of these functions is that they work with messages as an "indivisible" unit.  A message is assumed to be an arbitrary array/vector of bytes.  When sent, the entire message is sent as one unit.  When received, the entire message is returned exactly as it was sent.    This behavior is a bit different than a normal network socket where `send()` and `recv()` operations often introduce fragmentation and return partial data.

To solve this problem, you should have your functions work with size-prefixed data.  That is, all low-level I/O should embed a size field that indicates how many bytes of data comprise the message.  Functions such as `recv_message()` should use the size to know exactly how big the message is when it's received.

## Testing

Your `send_message()` and `recv_message()` functions should work with messages of arbitrary size.  Thus, you should test your functions with both small messages and large messages.   One way to test this is to write an echo server roughly like this:

```
import transport

def echo_server(sock):
    while True:
         msg = transport.recv_message(sock)
         transport.send_message(sock, msg)
```

Then, write an echo-client that tries different message sizes:

```
import transport

def echo_test(sock):
    for n in range(0, 8):
        msg = b'x'*(10**n)         # 1, 10, 100, 1000, 10000, bytes etc...
        transport.send_message(sock, msg)
        response = transport.recv_message(sock)
        assert msg == response
```

## Implementing a Key-Value Store

Using your message passing functions, your next task is to implement a networked key-value store.
A key value store is basically just a dictionary.  For example:

```
data = { }

def get(key):
    return data.get(key)

def set(key, value):
    data[key] = value

def delete(key):
    if key in data:
        del data[key]
```

Write a program `kvserver.py` that contains the key-value store data and responds to client messages.  You'll run the server as a standalone program like this:

```
bash % python kvserver.py 12345
KV Server listening on port 12345
```

Next, write a `kvclient.py` program that allows remote access to the server using an API like this:

```
import kvclient

kv = kvclient.KVClient(('localhost', 12345))    # Server address
kv.set('foo', 'hello')
kv.set('bar', 'world')
print(kv.get('foo'))    # --> Prints 'hello'
kv.delete('bar')
```

Here, the methods such as `kv.set()`, `kv.get()`, and `kv.delete()` will send messages to the server and return responses.

Hint: To solve this problem, you need to figure out what's in the message.  Perhaps you encode requests and responses in JSON, Python pickle, or some other encoding. 


