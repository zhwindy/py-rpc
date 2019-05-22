#!/usr/bin/env python
# encoding=utf-8
import socket
import struct
import json
import os

HOST, PORT = SERVER_ADDRESS = ('localhost', 8888)


def get_sock():
    """
    返回套接字
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(SERVER_ADDRESS)
    sock.listen()
    print(f"Socket server start at {HOST} {PORT}")
    return sock


def rpc_server(sock, handlers):
    """
    rpc 服务端
    """
    while True:
        client_conn, client_address = sock.accept()
        handle_conn(client_conn, client_address, handlers)


def handle_conn(client_conn, client_address, handlers):
    """
    处理链接
    """
    print(f"{client_address} is connecting")
    while True:
        data_len_bytes = client_conn.recv(4)
        if not data_len_bytes:
            break
        data_len, = struct.unpack("I", data_len_bytes)
        request_data = client_conn.recv(data_len)
        request = json.loads(request_data.decode())

        handle_requests(client_conn, request, handlers)

    print(f"{client_address} is gone")
    client_conn.close()


def handle_requests(conn, data, handlers):
    """
    处理请求
    """
    response = {
        "out": "400",
        "result": ""
    }
    if isinstance(data, dict):
        client_in = data["in"]
        client_params = data["params"]
        handlers[client_in](client_params)
        response['out'] = client_in
        response['result'] = "Success"
    else:
        response['result'] = "Request Error"

    data = json.dumps(response)
    data_len_bytes = struct.pack("I", len(data))
    conn.sendall(data_len_bytes)
    conn.sendall(data.encode())


def ping(data):
    """
    打印功能数据
    """
    print(data)


def prefork(n):
    """
    Preforking开启n个子进程
    """
    for _ in range(n):
        pid = os.fork()
        if pid < 0:
            return None
        elif pid == 0:
            break
        else:
            continue


if __name__ == "__main__":
    sock = get_sock()
    prefork(2)
    handlers = {
        "ping": ping
    }
    rpc_server(sock, handlers)
