# -*- coding: utf-8 -*-


# 商户数据服务
class DataService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def get_restaurant_sale_detail(self, shop_id, start_time, end_time):
        """
        查询指定时间段内单店营业数据汇总（历史数据）
        :param shopId:店铺Id
        :param startTime:查询起始日期
        :param endTime:查询结束日期
        """
        return self.__client.call("eleme.data.single.getRestaurantSaleDetail", {"shopId": shop_id, "startTime": start_time, "endTime": end_time})

    def get_restaurant_real_time_sale_detail(self, shop_id):
        """
        获取单店今日实时的营业数据汇总
        :param shopId:店铺Id
        """
        return self.__client.call("eleme.data.single.getRestaurantRealTimeSaleDetail", {"shopId": shop_id})

    def get_restaurant_sale_ratio(self, shop_id, start_time, end_time):
        """
        查询指定时间段内单店相关营业数据指标增长率
        :param shopId:店铺Id
        :param startTime:查询起始日期
        :param endTime:查询结束日期
        """
        return self.__client.call("eleme.data.single.getRestaurantSaleRatio", {"shopId": shop_id, "startTime": start_time, "endTime": end_time})

    def get_chain_restaurant_sale_detail(self, shop_ids, start_time, end_time):
        """
        查询指定时间段内连锁店营业数据汇总(历史数据)
        :param shopIds:连锁子店Id
        :param startTime:查询起始日期
        :param endTime:查询结束日期
        """
        return self.__client.call("eleme.data.chain.getChainRestaurantSaleDetail", {"shopIds": shop_ids, "startTime": start_time, "endTime": end_time})

    def get_chain_real_time_sale_detail(self, shop_ids):
        """
        获取连锁店今日实时的营业数据汇总
        :param shopIds:连锁子店Id
        """
        return self.__client.call("eleme.data.chain.getChainRealTimeSaleDetail", {"shopIds": shop_ids})

    def get_chain_restaurant_sale_ratio(self, shop_ids, start_time, end_time):
        """
        查询指定时间段内连锁店相关营业数据指标增长率
        :param shopIds:连锁子店Id
        :param startTime:查询起始日期
        :param endTime:查询结束日期
        """
        return self.__client.call("eleme.data.chain.getChainRestaurantSaleRatio", {"shopIds": shop_ids, "startTime": start_time, "endTime": end_time})

