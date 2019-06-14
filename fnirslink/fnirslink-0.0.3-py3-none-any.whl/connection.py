from fnirsLink.get_server_data import GetServerData
from fnirsLink.socket_server import SocketServer
from fnirsLink.web_request import WebRequest
from fnirsLink.url_name import UrlName
from fnirsLink.exception import CustomError
from fnirsLink.response import Response
import queue
import threading
import time

class Connection:
    BASEURL = "http://192.168.8.1:8080/fnirs";
    headers = {}
    server_data = GetServerData()
    thread = None

    def start(self):
        """
        开始测试
        :return:
        """
        url = self.BASEURL + UrlName.START
        para = {}
        try:
            WebRequest.post(url, para, self.headers)
            # 开启获取服务器数据线程
            self.start_thread()
            # 开启推送数据websocket
            server = SocketServer()
            server.start()
            return Response.success()
        except CustomError as e:
            return_data = Response.fail(1001 , e.error_info)
        return return_data

    def stop(self):
        """
        结束测试
        :return:
        """
        url = self.BASEURL + UrlName.STOP
        para = {}
        try:
            self.terminate()
            server = SocketServer()
            server.terminate()
            WebRequest.post(url, para, self.headers)
            return Response.success()
        except CustomError as e:
            return_data = Response.fail(1001 , e.error_info)
        return return_data

    def read_data(self):
        """
        获取服务器数据
        :return:
        """
        url = self.BASEURL + UrlName.READDATA
        para = {}

        try:
            data = WebRequest.get(url, para, self.headers)
            if data is not None:
                return Response.success_data(data['data'])
            else :
                return Response.success()
        except CustomError as e:
            return_data = Response.fail(1001 , e.error_info)
        return return_data

    def get_server_data(self):
        # 获取当前数据
        temp_data = self.read_data();
        if temp_data is None:
            return
        # 判断是否是字典类型
        if isinstance(temp_data,dict):
            if temp_data.__contains__('data') and temp_data['data'] is not None:
                self.server_data.data.put_nowait(temp_data['data'])

    def start_thread(self):
        self.thread = GetDataThread()
        self.thread.start()

    def terminate(self):
        if self.thread is not None:
            self.thread.stop()

class GetDataThread (threading.Thread):
    exit_flag = False
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'Thread-Get-Data'
        self.exit_flag = True
    def run(self):
        while self.exit_flag:
            Connection().get_server_data()
            time.sleep(0.5)
    def stop(self):
        self.exit_flag = False
