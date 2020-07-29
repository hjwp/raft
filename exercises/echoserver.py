import socket
import threading
import sys

HOST = '127.0.0.1'

def send_message(sock, msg):
    size_prefix = b'%12d' % len(msg)
    sock.sendall(size_prefix + msg)

def recv_message(sock):
    expected_size_bytes = sock.recv(12)
    assert len(expected_size_bytes) == 12
    expected_size = int(expected_size_bytes)
    msg = b''
    while len(msg) < expected_size:
        moar_bytes = sock.recv(65535)
        if not moar_bytes:
            break
        msg += moar_bytes
    assert len(msg) == expected_size
    return msg

def echo_server(conn, remote_port):
    with conn:
        print('starting echo server for connection', remote_port)
        while True:
            data = recv_message(conn)  # blocks until client sends sthing?
                                    # NB, will not close socket if KeyboardInterrupt at this point.
            if not data:
                # if data is empty (b''), then the client has disconnected
                print('ending server for connection', remote_port)
                return
            print(f'received message with length {len(data)}:\n\t{data[:50]}')
            send_message(conn, b'->' + data)

def main(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # need to call both bind() and listen(), otherwise
        # client will see `ConnectionRefusedError`
        # print('binding to', port, '\n\t', s)
        print('binding to', port)
        s.bind((HOST, port))  # may return OSError 98, address already in use
        print('listening on', port)
        s.listen()
        print("waiting to accept connection on", port)
        threads = []
        while True:
            conn, (_, remote_port) = s.accept()  # this hangs until someone connects
            print('got connection to', port, 'from port', remote_port)
            thread = threading.Thread(target=echo_server, args=(conn, remote_port))
            threads.append(thread)
            thread.start()

if __name__ == '__main__':
    main(int(sys.argv[1]))
