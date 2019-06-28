# -*- coding: utf-8 -*-


# 金融服务
class FinanceService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def query_balance(self, shop_id):
        """
        查询商户余额,返回可用余额和总余额
        :param shopId:饿了么店铺id
        """
        return self.__client.call("eleme.finance.queryBalance", {"shopId": shop_id})

    def query_balance_log(self, request):
        """
        查询余额流水,有流水改动的交易
        :param request:查询条件
        """
        return self.__client.call("eleme.finance.queryBalanceLog", {"request": request})

    def query_head_bills(self, shop_id, query):
        """
        查询总店账单
        :param shopId:饿了么总店店铺id
        :param query:查询条件
        """
        return self.__client.call("eleme.finance.queryHeadBills", {"shopId": shop_id, "query": query})

    def query_head_orders(self, shop_id, query):
        """
        查询总店订单
        :param shopId:饿了么总店店铺id
        :param query:查询条件
        """
        return self.__client.call("eleme.finance.queryHeadOrders", {"shopId": shop_id, "query": query})

    def query_branch_bills(self, shop_id, query):
        """
        查询分店账单
        :param shopId:饿了么分店店铺id
        :param query:查询条件
        """
        return self.__client.call("eleme.finance.queryBranchBills", {"shopId": shop_id, "query": query})

    def query_branch_orders(self, shop_id, query):
        """
        查询分店订单
        :param shopId:饿了么分店店铺id
        :param query:查询条件
        """
        return self.__client.call("eleme.finance.queryBranchOrders", {"shopId": shop_id, "query": query})

    def get_order(self, shop_id, order_id):
        """
        查询订单
        :param shopId:饿了么店铺id
        :param orderId:订单id
        """
        return self.__client.call("eleme.finance.getOrder", {"shopId": shop_id, "orderId": order_id})

