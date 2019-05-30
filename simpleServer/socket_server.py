#!/usr/bin/env python
# encoding=utf-8
import socket

HOST, PORT = SERVER_ADDRESS = ('localhost', 9999)


def rpc_server():
    """
    rpc 服务端
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(SERVER_ADDRESS)
    sock.listen()
    print(f"Socket server start at {HOST} {PORT}")

    while True:
        client_conn, client_address = sock.accept()
        request_data = client_conn.recv(1024)
        print(client_address, request_data)
        response = b"OK Request is success received!"
        client_conn.send(response)
        client_conn.close()


if __name__ == "__main__":
    rpc_server()
