# -*- coding:utf8 -*-

import threading
import time
from websocket import create_connection

from fnirsLink.connection import Connection

# 数据处理
class DataProcessing(threading.Thread):
    _ws = None
    running = False
    def __init__(self):
        super(DataProcessing, self).__init__()
        self.running = True
        try:
            self._ws = create_connection("ws://localhost:9000")
        except Exception as e:
            self._ws = None
            print('服务端未开启!')

    def run(self):
        if self._ws is None:
            return
        print('开始数据处理!')
        while self.running:
            result = self._ws.recv()##接收消息
            if result is not None:
                print(result)

if __name__ == '__main__':
    con = Connection()

    start = time.time()
    # 建立连接
    data = con.start();
    # 打印连接返回信息
    print(data);
    # 判断是否连接成功
    if data['success'] is True:
        end = time.time()
        # print(end - start) #打印平均响应时间

        # 开始读取数据
        # 启动数据处理线程
        thread = DataProcessing()
        thread.start()

        # 读取5s的数据
        time.sleep(100)
        thread.running = False
        # 结束测试
        data = con.stop();
        print(data);