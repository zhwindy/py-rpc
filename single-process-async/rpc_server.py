#!/usr/bin/env python
# encoding=utf-8
# 单进程异步服务器
import socket
import struct
import json
import asyncore
from io import StringIO


class RPCHandler(asyncore.dispatcher_with_send):
    """
    rpc处理器
    """
    def __init__(self, sock, addr):
        asyncore.dispatcher_with_send.__init__(self, sock=sock)
        self.addr = addr
        self.handlers = {
            "ping": self.ping
        }
        # 读数据缓冲区
        self.buf = StringIO()

    def handle_connect(self):
        print("Welcome", self.addr)

    def handle_read(self):
        while True:
            content = self.recv(1024)
            if content:
                self.buf.write(content.decode())
            if len(content) < 1024:
                break
        self.handle_rpc()
    
    def handle_rpc(self):
        while True:
            self.buf.seek(0)
            prefix_length = (self.buf.read(4)).encode()
            if len(prefix_length) < 4:
                break
            length, = struct.unpack("I", prefix_length)
            content = self.buf.read(length)
            if len(content) < length:
                break
            request = json.loads(content)
            client_in = request["in"]
            client_params = request["params"]
            handler = self.handlers[client_in]
            handler(client_in, client_params)
            
            left = self.buf.getvalue()[4 + length:]
            self.buf = StringIO()
            self.buf.write(left)

        self.buf.seek(0, 2)

    def handle_close(self):
        print("Goodbye {}".format(self.addr))
        self.close()

    def ping(self, method, params):
        print("{}{}".format(method, params))
        self.send_result(params)

    def send_result(self, params):
        response = {
            "out": "400",
            "result": ""
        }
        if isinstance(params, dict):
            response['out'] = params
            response['result'] = "Success"
        else:
            response['result'] = "Request Error"

        data = json.dumps(response)
        data_len_bytes = struct.pack("I", len(data))
        self.send(data_len_bytes)
        self.send(data.encode())


class RPCServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(1)

    def handle_accept(self):
        pair = self.accept()
        if pair:
            sock, addr = pair
            RPCHandler(sock, addr)


if __name__ == "__main__":
    RPCServer('localhost', 8888)
    print("Event Loop is starting")
    asyncore.loop()
