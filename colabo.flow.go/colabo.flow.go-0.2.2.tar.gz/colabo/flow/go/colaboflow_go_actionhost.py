# -*- coding: utf-8 -*-
#!/usr/bin/python

from __future__ import print_function
import time
import random
from concurrent import futures
from datetime import datetime
# import dateutil.parser

import grpc

from . import go_pb2
from . import go_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class ColaboFlowGoActionHost():
    def __init__(self, actionsHostServicerImplementationClass, socketUrl=None, concurrentThreadsNo=10):

        print("ColaboFlowGoActionHost::__init__")

        if not socketUrl:
            socketUrl = 'localhost:50801'
        self.socketUrl = socketUrl
        
        self.concurrentThreadsNo = concurrentThreadsNo

        # Start server with 10 concurrent threads
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.concurrentThreadsNo))
        go_pb2_grpc.add_ActionsHostServicer_to_server(
            actionsHostServicerImplementationClass(), self.server)
        self.server.add_insecure_port(self.socketUrl)
    
    def startService(self):
        global _ONE_DAY_IN_SECONDS
        self.server.start()
        print("ColaboFlowGoActionHost::startService: started listening on: %s" % (
            self.socketUrl))
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            self.server.stop(0)
