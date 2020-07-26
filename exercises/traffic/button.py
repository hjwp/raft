# button.py
#
# This program is an internet push-button.  When you press return on
# the keyboard, it sends a UDP message to a host/port of your
# choice. That's all it does.
#
# Here's an example of code that uses it
#
#    >>> from socket import socket, AF_INET, SOCK_DGRAM
#    >>> sock = socket(AF_INET, SOCK_DGRAM)
#    >>> sock.bind(('', 12000))
#    >>> while True:
#    ...     msg, addr = sock.recvfrom(1024)
#    ...     print("You pressed it")
#    ...
#
# With that running, go run this program in a separate terminal
# using 'python button.py localhost 12000'.  Hit return a few
# times.  You should see the above message being printed.

from socket import socket, AF_INET, SOCK_DGRAM
import sys

def main(host, port):
    sock = socket(AF_INET, SOCK_DGRAM)
    with sock:
        while True:
            try:
                line = input("Button: [Press Return]")
            except EOFError:
                return
            try:
                sock.sendto(b"press", (host, port))
            except OSError:
                print("Error: Not connected")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(f'Usage: {sys.argv[0]} host port')
    main(sys.argv[1], int(sys.argv[2]))


        
    
