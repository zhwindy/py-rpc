#!/usr/bin/env python
# encoding=utf-8
import socket

HOST, PORT = SERVER_ADDRESS = ('localhost', 9999)


def rpc_client():
    """
    rpc客户端
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(ADDRESS)
    sock.send(b"this is request from rpc_client")

    result = sock.recv(1024)
    print(result)
    sock.close()


if __name__ == "__main__":
    rpc_client()
