# -*- coding:utf8 -*-

import threading
import hashlib
import socket
import base64
import time

from fnirsLink.get_server_data import GetServerData


class SocketServer(object):
    _instance_lock = threading.Lock()
    clients = {}
    port = 9000
    _socket = None
    server = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(SocketServer, "_instance"):
            with SocketServer._instance_lock:
                if not hasattr(SocketServer, "_instance"):
                    SocketServer._instance = object.__new__(cls)
        return SocketServer._instance

    def start(self):
        self.server = SocketServerThread()
        self.server.start()

    def terminate(self):
        self.server.stop()
        # self._socket.close()

    # 通知客户端
    def notify(self , message):
        import struct

        token = b"\x81"
        length = len(message)
        if length < 126:
            token += struct.pack("B", length)
        elif length <= 0xFFFF:
            token += struct.pack("!BH", 126, length)
        else:
            token += struct.pack("!BQ", 127, length)

        msg = token + message
        for connection in self.clients.values():
            connection.send(msg)

# 服务端
class SocketServerThread(threading.Thread):
    def __init__(self):
        super(SocketServerThread, self).__init__()
        self.running = True
        self.thread = None

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', SocketServer.port))
        sock.listen(5)
        # print('websocket server started!')
        while self.running:
            connection, address = sock.accept()
            try:
                username = "ID" + str(address[1])
                self.thread = SocketServerClient(connection, username)
                self.thread.start()
                SocketServer.clients[username] = connection
            except socket.timeout:
                print('websocket connection timeout!')

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.stop()



# 客户端处理线程
class SocketServerClient(threading.Thread):
    def __init__(self, connection, username):
        super(SocketServerClient, self).__init__()
        self.connection = connection
        self.username = username
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        print('new websocket client joined!')
        data = self.connection.recv(1024)
        headers = self.parse_headers(data)
        token = self.generate_token(headers['Sec-WebSocket-Key'])
        response_tpl = "HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n" \
                       "Upgrade:websocket\r\n" \
                       "Connection:Upgrade\r\n" \
                       "Sec-WebSocket-Accept:%s\r\n" \
                       "WebSocket-Location:ws://%s%s\r\n\r\n"
        response_str = response_tpl % (token.decode('utf-8'), headers['Host'], headers['url'])
        self.connection.send(bytes(response_str, encoding='utf-8'))
        get_server_data = GetServerData()
        while self.running:
            data = get_server_data.get_single_time_data()
            # print('data',data)
            if data is None:
                continue
            # message = self.username + ": " + str(data)
            message = str(data)
            SocketServer().notify(message.encode('utf-8'))
            time.sleep(0.1)

    def parse_data(self, msg):
        # v = ord(msg[1]) & 0x7f
        v = msg[1] & 0x7f
        if v == 0x7e:
            p = 4
        elif v == 0x7f:
            p = 10
        else:
            p = 2
        mask = msg[p:p + 4]
        data = msg[p + 4:]
        # return ''.join([chr(ord(v) ^ ord(mask[k%4])) for k, v in enumerate(data)])
        return ''.join([chr(v ^ mask[k % 4]) for k, v in enumerate(data)])

    def parse_headers(self, msg):
        """
        将请求头格式化成字典
        :param data:
        :return:
        """
        header_dict = {}
        data = str(msg, encoding='utf-8')

        header, body = data.split('\r\n\r\n', 1)
        header_list = header.split('\r\n')
        for i in range(0, len(header_list)):
            if i == 0:
                if len(header_list[i].split(' ')) == 3:
                    header_dict['method'], header_dict['url'], header_dict['protocol'] = header_list[i].split(' ')
            else:
                k, v = header_list[i].split(':', 1)
                header_dict[k] = v.strip()
        return header_dict

    def generate_token(self, msg):
        key = msg + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        ser_key = hashlib.sha1(key.encode('utf-8')).digest()
        return base64.b64encode(ser_key)

# obj1 = SocketServer()
# obj2 = SocketServer()
# print(obj1,obj2)
# obj1.start()
# obj2.start()
#
# def task(arg):
#     obj = SocketServer()
#     print(obj)
#
# for i in range(10):
#     t = threading.Thread(target=task,args=[i,])
#     t.start()