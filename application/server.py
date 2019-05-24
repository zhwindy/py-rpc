#!/usr/bin/env python
# encoding=utf-8
import os
import sys
import signal
import socket
import struct
import asyncore
import math
import json
import errno
from io import BytesIO
from kazoo.client import KazooClient


class RPCHandler(asyncore.dispatcher_with_send):

    def __init__(self, sock, addr):
        asyncore.dispatcher_with_send.__init__(self, sock=sock)
        self.addr = addr
        self.handlers = {
            "ping": self.ping,
            "calc": self.calc,
        }
        self.buff = BytesIO()
    
    def handle_connect(self):
        print("Welcome client {}".format(self.addr))
    
    def handle_read(self):
        """
        接收请求数据,写入读缓存
        """
        while True:
            content = self.recv(1024)
            if content:
                self.buff.write(content)
            if len(content) < 1024:
                break

        self.handle_rpc()
    
    def handle_rpc(self):
        """
        处理请求
        """
        while True:
            self.buff.seek(0)
            length_bytes = self.buff.read(4)
            if len(length_bytes) < 4:
                break
            length, = struct.unpack("I", length_bytes)
            content = self.buff.read(length)
            if len(content) < length:
                break
            data = json.loads(content.decode())
            method, params = data.values()
            handler = self.handlers[method]
            handler(method, params)

            left = self.buff.getvalue()[length + 4:]
            self.buff = BytesIO()
            self.buff.write(left)

        self.buff.seek(0, 2)
    
    def handle_close(self):
        print("Goodbye client {}".format(self.addr))
        self.close()
    
    def ping(self, method, params):
        """
        处理方法
        """
        print("exxcute {} with params {}".format(method, params))
        self.response_result(method, params)

    def calc(self, method, params):
        s = 0.0
        n = int(params)
        for i in range(n + 1):
            s += 1.0 / (2 * i + 1) / (2 * i + 1)
        result = math.sqrt(8 * s)
        self.response_result(method, result)
    
    def response_result(self, method, data):
        """
        响应结果
        """
        response = {"out": method, "result": ""}
        if data:
            response['result'] = data
        result = json.dumps(response)
        prefix_length = struct.pack("I", len(result))
        self.send(prefix_length)
        self.send(result.encode())


class RPCServer(asyncore.dispatcher):

    zk_root = "/demo"
    zk_rpc = zk_root + "/rpc"

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.host = host
        self.port = port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(1)
        self.child_pids = []
        if self.prefork(5):
            self.register_zk()
            self.register_parent_signal()
        else:
            self.register_child_signal()
    
    def prefork(self, n):
        for _ in range(n):
            pid = os.fork()
            if pid < 0:
                raise Exception("fork error")
            if pid == 0:
                return False
            if pid > 0:
                self.child_pids.append(pid)
                continue
        return True
    
    def register_zk(self):
        self.zk = KazooClient(hosts="127.0.0.1:2181")
        self.zk.start()

        self.zk.ensure_path(self.zk_root)
        value = json.dumps({"host": self.host, "port": self.port})
        self.zk.create(self.zk_rpc, value=value.encode(), ephemeral=True, sequence=True)
    
    def register_parent_signal(self):
        """
        设置父进程信号处理函数
        """
        signal.signal(signal.SIGINT, self.exit_parent)
        signal.signal(signal.SIGTERM, self.exit_parent)
        signal.signal(signal.SIGCHLD, self.kill_child)
    
    def register_child_signal(self):
        """
        设置子进程信号处理函数
        """
        signal.signal(signal.SIGINT, self.exit_child)
        signal.signal(signal.SIGTERM, self.exit_child)
    
    def exit_child(self, signum, frame):
        """
        子进程退出
        """
        self.close()
        asyncore.close_all()
        print("All closed!")
        os._exit(0)

    def exit_parent(self, signum, frame):
        """
        处理父进程退出
        """
        self.zk.stop()
        self.close()
        asyncore.close_all()
        pids = []
        for pid in self.child_pids:
            print(f"Before kill child process {pid}")
            try:
                os.kill(pid, signal.SIGINT)
                pids.append(pid)
            except OSError as ex:
                if ex.args[0] == errno.ECHILD:
                    continue
                else:
                    raise Exception(ex)
            print(f"End kill child process {pid}")

        for pid in pids:
            while True:
                try:
                    os.waitpid(pid, 0)
                    break
                except Exception as ex:
                    if ex.args[0] == errno.ECHILD:
                        break
                    if ex.args[0] == errno.EINTR:
                        continue
                    else:
                        raise Exception(ex)
            print(f"wait over {pid}")

        os._exit(0)

    def kill_child(self, signum, frame):
        """
        收割子进程
        """
        print("Start kill child process")
        while True:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
            except OSError as ex:
                if ex.args[0] == errno.ECHILD:
                    break
                if ex.args[0] == errno.EINTR:
                    continue
                else:
                    raise Exception(ex)
            if pid == 0:
                print("没有可以收割的子进程,退出")
                break
            else:
                try:
                    self.child_pids.remove(pid)
                except ValueError:
                    pass
        print("end kill child process")

    def handle_accept(self):
        pair = self.accept()
        if pair:
            conn, addr = pair
            RPCHandler(conn, addr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        host = '127.0.0.1'
        port = 8888
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
    RPCServer(host, port)
    print("RPC SERVER starting...")
    asyncore.loop()
