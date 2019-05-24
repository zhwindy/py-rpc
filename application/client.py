#!/usr/bin/env python
# encoding=utf-8
import time
import random
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
        """
        发起连接
        """
        host, port = self.addr.split(":")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, int(port)))
    
    def ping(self, facebook):
        print("ping server {}".format(facebook))
        return self.rpc("ping", facebook)
    
    def calc(self, n):
        print("calc {}".format(n))
        return self.rpc("calc", n)
    
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

        response_prefix_length = sock.recv(4)
        prefix_length, = struct.unpack("I", response_prefix_length)
        response_data = sock.recv(prefix_length)
        response_content = json.loads(response_data.decode())

        return response_content['out'], response_content['result']
    
    def reconnect(self):
        """
        重连
        """
        if self._socket:
            self._socket.close()
            self._socket = None
        self.connect()


def get_servers():
    zk = KazooClient(hosts="127.0.0.1:2181")
    zk.start()

    current_addrs = set()

    def watch_server(*args):
        """
        监听服务器列表变化
        """
        new_addrs = set()
        for child in zk.get_children(zk_root, watch_server):
            node = zk.get(zk_root + "/" + child)
            data = json.loads(node[0])
            new_addrs.add("{}:{}".format(data['host'], data['port']))
        
        new_servers = new_addrs - current_addrs
        remove_servers = current_addrs - new_addrs

        del_servers = []
        for address in remove_servers:
            for s in G['servers']:
                if address == s.addr:
                    del_servers.append(s)
                    break
        
        for server in del_servers:
            G['servers'].remove(server)
            current_addrs.remove(server.addr)
        
        for addr in new_servers:
            G['servers'].append(RemoteServer(addr))
            current_addrs.add(addr)
        
    for child in zk.get_children(zk_root, watch=watch_server):
        node = zk.get(zk_root + "/" + child)
        data = json.loads(node[0])
        current_addrs.add("{}:{}".format(data['host'], data['port']))
    G['servers'] = [RemoteServer(addr) for addr in current_addrs]

    return G['servers']


def get_random_server():
    """
    随机选择服务器
    """
    if G['servers'] is None:
        get_servers()
    if not G['servers']:
        return
    server = random.choice(G['servers'])

    return server


if __name__ == "__main__":
    for i in range(50):
        server = get_random_server()
        if not server:
            break
        time.sleep(1)
        out, result = server.ping(f"www.baidu.com {i}")
        print("Server address {}, response: {} {}".format(server.addr, out, result))

        server = get_random_server()
        if not server:
            break
        time.sleep(1)
        out, result = server.calc(i)
        print("Server address {}, response: {} {}".format(server.addr, out, result))
