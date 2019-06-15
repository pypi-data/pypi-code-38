# -*- coding: utf-8 -*-
#!/usr/bin/python

from __future__ import print_function

import random

from datetime import datetime
# import dateutil.parser

import grpc

from . import go_pb2
from . import go_pb2_grpc

class ColaboFlowGo():
    goRequestDefault = None
    stubDefault = None

    def __init__(self, socketUrl=None, reuseClient=True):
        
        print("ColaboFlowGo::__init__")

        if not socketUrl:
            socketUrl = 'localhost:50506'
        self.socketUrl = socketUrl

        # create new stub client only if requested or
        # there is no defualt stub client one yet
        if not reuseClient or not ColaboFlowGo.stubDefault:
            print("Initializing gRPC at: %s" % (socketUrl))
            self.channel = grpc.insecure_channel(socketUrl)
            # to call service methods, we first need to create a stub.
            print(go_pb2_grpc)
            self.stub = go_pb2_grpc.FlowsHostStub(self.channel)
            ColaboFlowGo.stubDefault = self.stub
        else:
            self.stub = ColaboFlowGo.stubDefault



    def executeActionSync(self, actionExecuteRequest):
        actionExecuteReply = self.stub.executeActionSync(actionExecuteRequest)
        if not actionExecuteReply.id:
            print("Server returned incomplete actionExecuteReply")
        else:
            print("actionExecuteReply is %s" % (actionExecuteReply))
        return actionExecuteReply
