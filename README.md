## 用python一步一步搭建高并发rpc服务

#### 开发环境
```
系统: MacOSX 10.14.4
语言: python 3.7.2
```

#### 潜心修炼: RPC服务器探究分7个阶段循序渐进

由简单到复杂,由单进程到高并发

1. 单线程同步
```
由单进程-单线程的方式服务
文件: 001_single_thread_sync.py
```
2. 多线程同步
```
由主进程-开启多线程方式服务
文件: 002_multi_thread_sync.py
```
3. 多进程同步
```
主进程收到客户端链接后fork出子进程为客户端提供服务
文件: 003_multi_process_sync.py
```
4. PreForking多进程同步
```
预先fork出多个进程共同监听套接字提供服务
文件: 004_preforking_process_sync.py
多进程+多线程: 005_preforking_process_multi_threads_sync.py
```
5. 单进程异步
```
非阻塞IO/事件监听,单进程异步服务
文件: 006_single_process_async.py
```
6. PreForking多进程异步
```
预先fork出多个进程,每个进程内都采用异步的方式提供服务
文件: 007_preforking_process_async.py
```
7. 多进程传递文件描述符(同步)
```
采用Node cluster多进程模型,由master进程传递fd给slave进程处理. 避免了多个salve竞争处理导致的`马太效应`
文件: 008_multi_process_node_cluster.py
```

#### 实战演练: 开发一个简单的分布式高并发RPC服务器application

服务器端: server.py

打开一个终端,启动服务
```
python server.py 127.0.0.1 8888
```

再打开一个终端,启动第二个服务
```
python server.py 127.0.0.1 8889
```

客户端: client.py