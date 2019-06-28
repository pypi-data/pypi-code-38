# -*- coding: utf-8 -*-


# 服务市场服务
class MarketService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def sync_market_messages(self, start, end, offset, limit):
        """
        同步某一段时间内的服务市场消息
        :param start:开始时间
        :param end:结束时间
        :param offset:消息偏移量
        :param limit:查询消息数
        """
        return self.__client.call("eleme.market.syncMarketMessages", {"start": start, "end": end, "offset": offset, "limit": limit})

    def create_order(self, request):
        """
        创建内购项目订单
        :param request:创建订单请求信息
        """
        return self.__client.call("eleme.market.createOrder", {"request": request})

    def query_order(self, order_no):
        """
        查询服务市场订单
        :param orderNo:服务市场订单编号
        """
        return self.__client.call("eleme.market.queryOrder", {"orderNo": order_no})

