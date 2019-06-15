# -*- coding: utf-8 -*-
#!/usr/bin/python

from __future__ import print_function

import random

import grpc
from datetime import datetime
import dateutil.parser

from . import audit_pb2
from . import audit_pb2_grpc

class ColaboFlowAudit():
    auditRequestDefault = None
    stubDefault = None

    def __init__(self, socketUrl=None, defaultAuditRequest = None, reuseClient = True):
        # NOTE(gRPC Python Team): .close() is possible on a channel and should be
        # used in circumstances in which the with statement does not fit the needs
        # of the code.
        
        print("ColaboFlowAudit::__init__");

        if not socketUrl:
            socketUrl = 'localhost:50505'
        self.socketUrl = socketUrl

        # create new stub client only if requested or
        # there is no defualt stub client one yet
        if not reuseClient or not ColaboFlowAudit.stubDefault:
            print("Initializing gRPC at: %s" % (socketUrl))
            self.channel = grpc.insecure_channel(socketUrl)
            # to call service methods, we first need to create a stub.
            self.stub = audit_pb2_grpc.AuditStub(self.channel)
            ColaboFlowAudit.stubDefault = self.stub
        else:
            self.stub = ColaboFlowAudit.stubDefault

        if defaultAuditRequest:
            ColaboFlowAudit.auditRequestDefault = defaultAuditRequest
            print("auditRequestDefault: %s " % ColaboFlowAudit.auditRequestDefault)

    def getDefaultRequest(self):
        return ColaboFlowAudit.auditRequestDefault

    def setDefaultValues(self, dA, a):
        if not a.bpmn_type and dA.bpmn_type:
            a.bpmn_type = dA.bpmn_type
        if not a.bpmn_subtype and dA.bpmn_subtype:
            a.bpmn_subtype = dA.bpmn_subtype
        if not a.bpmn_subsubtype and dA.bpmn_subsubtype:
            a.bpmn_subsubtype = dA.bpmn_subsubtype

        if not a.flowId and dA.flowId:
            a.flowId = dA.flowId
        if not a.name and dA.name:
            a.name = dA.name

        if not a.userId and dA.userId:
            a.userId = dA.userId
        if not a.sessionId and dA.sessionId:
            a.sessionId = dA.sessionId
        if not a.flowInstanceId and dA.flowInstanceId:
            a.flowInstanceId = dA.flowInstanceId

        if not a.implementationId and dA.implementationId:
            a.implementationId = dA.implementationId
        if not a.implementerId and dA.implementerId: 
            a.implementerId = dA.implementerId

    def audit_create_and_finish(self, auditRequest, success=True):
        self.audit_create(auditRequest);
        auditReply = self.audit_finish(auditRequest, success=True, time=0)
        return auditReply;

    def audit_create(self, auditRequest):
        self.setDefaultValues(ColaboFlowAudit.auditRequestDefault, auditRequest)
        auditRequest.startTime = datetime.now().isoformat()
        auditReply = None
        # auditReply = self.stub.submit(auditRequest)
        # if not auditReply.id or not auditReply.time:
        #     print("Server returned incomplete auditReply")
        # else:
        #     print("Audit result is %s" % (auditReply))
        return auditReply

    def audit_finish(self, auditRequest, success=True, time=None):
        auditRequest.success = success;
        if time == None:
            # https://stackoverflow.com/questions/766335/python-speed-testing-time-difference-milliseconds
            # https://stackoverflow.com/questions/28331512/how-to-convert-pythons-isoformat-string-back-into-datetime-object
            # https://stackoverflow.com/questions/10197859/python-serializing-deserializing-datetime-time
            startTimeStr = auditRequest.startTime
            startTime = dateutil.parser.parse(startTimeStr)
            endTime = datetime.now()
            deltaTime = endTime - startTime
            time = deltaTime.seconds*1000000+deltaTime.microseconds
            auditRequest.time = str(time) # in microseconds
            auditRequest.endTime = endTime.isoformat()
        else:
            auditRequest.endTime = auditRequest.startTime
            auditRequest.time = str(0)
        self.setDefaultValues(
            ColaboFlowAudit.auditRequestDefault, auditRequest)

        auditReply = self.stub.submit(auditRequest)
        if not auditReply.id or not auditReply.time:
            print("Server returned incomplete auditReply")
        else:
            print("Audit result is %s" % (auditReply))
        return auditReply
