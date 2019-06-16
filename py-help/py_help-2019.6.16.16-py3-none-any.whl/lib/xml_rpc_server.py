# -*- coding: utf-8 -*-
import rpyc
import sys
import os
from rpyc.utils.server import ThreadedServer
from .CommonLogger import debug, info, warn, error
import json
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn


class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class XmlRpcServer:
    host_ip = '0.0.0.0'
    port = 8080
    url = '/RPC2'

    def __init__(self, host_ip='0.0.0.0', port=8080, url='/RPC2'):
        self.host_ip = host_ip
        self.port = port
        self.url = url
        self.server_instance = ThreadXMLRPCServer((host_ip, port), allow_none=True)
        self.server_instance.register_instance(self)

    def start_server(self):
        self.server_instance.serve_forever()

    def ping(self):
        return 'pong'

    def get_home(self):
        return os.path.expanduser('~')

    def realtime_read(self):
        pass

    def read(self):
        pass

    def run_keyword(self, keyword, data, timeout, async):
        debug("要运行keyword:{},参数是:{},timeout:{},async:{}".format(keyword, data, timeout, async))

    def stop_keyword(self):
        pass

    def shutdown(self):
        self.server_instance.shutdown()
        return 'done'
