#!/usr/bin/env python
# encoding=utf-8
import time
import json
import struct
import socket
from kazoo.client import KazooClient

zk_root = "/demo"

G = {"servers": None}


class RemoteServer(object):
    """
    服务封装
    """
    def __init__(self, addr):
        self.addr = addr
        self._socket = None
    
    @property
    def socket(self):
        if not self._socket:
            self.connect()
        return self._socket
    
    def connect(self):
        host, port = self.addr.split(":")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
    
    def ping(self, facebook):
        print("ping server {}".format(facebook))
        self.rpc("ping", facebook)
    
    def calc(self, n):
        print("calc {}".format(n))
        self.rpc("calc", n)
    
    def rpc(self, _in, params):
        """
        发起rpc请求,接收rpc-server响应
        """
        sock = self.socket
        request = {"in": _in, "params": params}
        content = json.dumps(request)
        prefix_length = struct.pack("I", len(content))
        sock.send(prefix_length)
        sock.sendall(content.encode())


if __name__ == "__main__":
    pass
