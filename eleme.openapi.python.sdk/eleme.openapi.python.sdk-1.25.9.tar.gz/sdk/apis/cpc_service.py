# -*- coding: utf-8 -*-


# CPC竞价服务
class CpcService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def get_all_balance(self, shop_id):
        """
        查询余额
        :param shopId:店铺ID
        """
        return self.__client.call("eleme.cpc.getAllBalance", {"shopId": shop_id})

    def check_shop_certification(self, shop_id):
        """
        确认店铺两证是否齐全
        :param shopId:店铺ID
        """
        return self.__client.call("eleme.cpc.checkShopCertification", {"shopId": shop_id})

    def get_wager_information(self, shop_id):
        """
        查询推广信息
        :param shopId:店铺ID
        """
        return self.__client.call("eleme.cpc.getWagerInformation", {"shopId": shop_id})

    def get_wager_estimate(self, shop_id, bid):
        """
        根据出价查询预估信息
        :param shopId:店铺ID
        :param bid:CPC出价
        """
        return self.__client.call("eleme.cpc.getWagerEstimate", {"shopId": shop_id, "bid": bid})

    def get_suggest_wager_info(self, shop_id):
        """
        查询推荐价格、预估信息
        :param shopId:店铺ID
        """
        return self.__client.call("eleme.cpc.getSuggestWagerInfo", {"shopId": shop_id})

    def get_residue_degree(self, shop_id):
        """
        查询推广修改剩余次数
        :param shopId:店铺ID
        """
        return self.__client.call("eleme.cpc.getResidueDegree", {"shopId": shop_id})

    def update_wager_status(self, shop_id, status):
        """
        设置推广状态
        :param shopId:店铺ID
        :param status:推广状态
        """
        return self.__client.call("eleme.cpc.updateWagerStatus", {"shopId": shop_id, "status": status})

    def set_wager_grade(self, shop_id, bid):
        """
        设置推广出价
        :param shopId:店铺ID
        :param bid:要设置的出价(元)
        """
        return self.__client.call("eleme.cpc.setWagerGrade", {"shopId": shop_id, "bid": bid})

    def set_wager_budget(self, shop_id, budget):
        """
        设置预算
        :param shopId:店铺ID
        :param budget:要设置的预算(元)
        """
        return self.__client.call("eleme.cpc.setWagerBudget", {"shopId": shop_id, "budget": budget})

    def update_auto_status(self, shop_id, auto_status, launch_hours):
        """
        更新自动投放状态
        :param shopId:店铺ID
        :param autoStatus:操作状态
        :param launchHours:小时集合
        """
        return self.__client.call("eleme.cpc.updateAutoStatus", {"shopId": shop_id, "autoStatus": auto_status, "launchHours": launch_hours})

    def set_wager_speed(self, shop_id, wager_speed_mode):
        """
        设置推广速率
        :param shopId:店铺ID
        :param wagerSpeedMode:速率类型
        """
        return self.__client.call("eleme.cpc.setWagerSpeed", {"shopId": shop_id, "wagerSpeedMode": wager_speed_mode})

    def get_actual_ranking(self, shop_id):
        """
        获取竞价推广实时排名
        :param shopId:店铺ID
        """
        return self.__client.call("eleme.cpc.getActualRanking", {"shopId": shop_id})

    def get_u_v_summary(self, shop_id, begin_date, end_date):
        """
        查询推广效果数据
        :param shopId:店铺ID
        :param beginDate:开始时间
        :param endDate:结束时间
        """
        return self.__client.call("eleme.cpc.getUVSummary", {"shopId": shop_id, "beginDate": begin_date, "endDate": end_date})

    def get_rank_and_cost_info(self, shop_id, begin_date, end_date):
        """
        查询推广点击分布信息
        :param shopId:店铺ID
        :param beginDate:开始时间
        :param endDate:结束时间
        """
        return self.__client.call("eleme.cpc.getRankAndCostInfo", {"shopId": shop_id, "beginDate": begin_date, "endDate": end_date})

    def get_user_distribution(self, shop_id, date):
        """
        获取推广活跃顾客的点击结构
        :param shopId:店铺ID
        :param date:时间
        """
        return self.__client.call("eleme.cpc.getUserDistribution", {"shopId": shop_id, "date": date})

