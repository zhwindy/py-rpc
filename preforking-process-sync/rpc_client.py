#!/usr/bin/env python
# encoding=utf-8
import socket
import time
import struct
import json

HOST, PORT = ADDRESS = ('localhost', 8888)


def rpc_client(sock, data):
    """
    发起rpc请求到rpc-server并打印响应
    """
    msg_json = json.dumps(data)
    msg_len = int(len(msg_json))
    msg_prefix_len = struct.pack("I", msg_len)

    # 发送请求
    sock.sendall(msg_prefix_len)
    sock.sendall(msg_json.encode())

    # 接收响应
    prefix_bytes = sock.recv(4)
    response_len, = struct.unpack("I", prefix_bytes)
    response_body = sock.recv(response_len)
    response = json.loads(response_body)

    print("RPC-Server Response:", response_len, response)


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(ADDRESS)
    for i in range(10):
        request_data = {"in": "ping", "params": f"www.baidu.com {i}"}
        rpc_client(sock, request_data)
        time.sleep(6)
    sock.close()
