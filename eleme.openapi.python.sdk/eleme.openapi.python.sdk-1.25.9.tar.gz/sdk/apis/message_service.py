# -*- coding: utf-8 -*-


# 消息服务
class MessageService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def get_non_reached_messages(self, app_id):
        """
        获取未到达的推送消息
        :param appId:应用ID
        """
        return self.__client.call("eleme.message.getNonReachedMessages", {"appId": app_id})

    def get_non_reached_o_messages(self, app_id):
        """
        获取未到达的推送消息实体
        :param appId:应用ID
        """
        return self.__client.call("eleme.message.getNonReachedOMessages", {"appId": app_id})

