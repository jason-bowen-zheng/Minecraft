import json
import socket
import time
from threading import Thread

from server.client import Client
from server.utils import *

class Server():

    def __init__(self):
        self.thread = {}
        self.thread_count = -1

    def start(self):
        # 开启服务器
        log_info('start server')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('localhost', 32768))
        self.socket.listen(1)
        while True:
            try:
                conn, addr = self.socket.accept()
            except:
                log_info('server stopped')
                break
            self.thread_count += 1
            self.thread[self.thread_count] = Thread(target=self.client, args=(conn, addr),
                    name='t{0}'.format(self.thread_count))
            log_info('new connection @ %s:%d, total %d thread(s)' % (addr[0], addr[1], self.thread_count + 1))
            self.thread[self.thread_count].start()

    def client(self, conn, addr):
        # 客户端连接
        log_info('new client thread')
        # 互换版本号
        # 发送: server {"version": VERSION}
        conn.send('server {0}'.format(json.dumps({'version': VERSION})).encode())
        version = conn.recv(1024).decode()
        # 期望接收到: client {"version": VERSION}
        if version.startswith('client '):
            try:
                client_ver = json.loads(version[7:])['version']
            except:
                log_info('unknow client version: %s' % version[7:])
                conn.send('refused'.encode())
                conn.close()
                return
            else:
                # 接收到正确版本
                log_info('client version: %s' % client_ver)
                conn.send('welcome'.encode())
        else:
            conn.send('refused'.encode())
            conn.close()
            return
        # 请求玩家名称及 UUID
        conn.send('get_player'.encode())
        player = conn.recv(1024).decode()
        if player.startswith('player '):
            try:
                player = json.loads(player[7:])
            except:
                log_info('unknow player: %s' % player)
                conn.send('refused'.encode())
                conn.close()
                return
            else:
                # 接收到正确的玩家数据
                log_info('new player: id: %s, name: %s' % (player['id'], player['name']))
                conn.send('welcome {0}'.format(player['name']).encode())
        else:
            conn.send('refused'.encode())
            conn.close()
            return
        client = Client(conn, addr, client_ver, player)