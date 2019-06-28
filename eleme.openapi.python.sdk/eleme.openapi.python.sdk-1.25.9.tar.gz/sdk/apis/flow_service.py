# -*- coding: utf-8 -*-


# 餐厅入口流量服务
class FlowService:

    __client = None

    def __init__(self, client):
        self.__client = client

