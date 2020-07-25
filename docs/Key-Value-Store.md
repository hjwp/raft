# Exercise : Key-Value Store

A common kind of distributed service is that of a key-value store (e.g., memcache, redis, etc.).  A key-value is basically a Python dictionary. For example:

```
 # The held data
 data = { }
 
 # Functions for modifying the data
 def get(key):
     return data[key]
 
 def set(key, value):
     data[key] = value
 
 def delete(key):
     del data[key]
 
```

## Putting it on the network
 
Take the above key-value store code and figure out some way to make it work over the network.  The data will be held on a server which will sit and wait for client connections.  Clients will send messages that encode one of the three operations (get, set, delete). The server will carry out the operation and send a response back to the client.

The server will take the above code and add some networking. For example:

```
data = { }

# Functions for modifying the data
def get(key):
    return data[key]
 
def set(key, value):
    data[key] = value
 
def delete(key):
    del data[key]

def run_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(address)
    sock.listen(1)
    while True:
        client, addr = sock.accept()
        handle_client(client)

def handle_client(client):
    # Read command from client
    ...
    # Send response to client

if __name__ == '__main__':
   run_server(('', 30000))
```

On the client, create a nice class that hides the low-level details. For example:

```
from kvclient import KVClient     # You need to write
 
client = KVClient('localhost', 30000) 
client.set('key', 'value')        # Set a key
v = client.get('key')             # Get a key
client.delete('key')              # Delete a key
...
client.close()                    # Close the connection
```

To make this work, you're going to need to figure out some mechanism for sending messages back and forth between the server and client. The messages need to encode the requested operation (get, set, delete) along with any other arguments (key and value). You can assume that both the key and value are strings.

Don't overthink the implementation. It's not necessary to make anything super-advanced. It's not a website. You don't need to use some giant framework to implement it. If possible, you should try to do it by extending the code used in the socket exercise.

## Concurrent clients

For improved performance, it is useful for a client and a server to maintain a persistent connection (i.e., an active socket that just stays connected).  However, if you do that, you'll run into problems if the code needs to support more than one client at once.  How would you modify the code to support multiple client connections?
