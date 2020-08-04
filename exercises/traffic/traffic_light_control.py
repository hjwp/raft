import time
import threading
import queue
from socket import socket, AF_INET, SOCK_DGRAM

NS_PORT = 12001
EW_PORT = 12002
BUTTON_PORT = 12003

def ticker(q):
    while True:
        q.put('tick')
        time.sleep(1)

def button_listener(q):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('', BUTTON_PORT))
    while True:
         msg, addr = sock.recvfrom(1024)
         q.put('button press')

def main() -> None:
    q = queue.Queue()
    threading.Thread(target=ticker, args=(q,)).start()
    threading.Thread(target=button_listener, args=(q,)).start()

if __name__ == '__main__':
    main()
