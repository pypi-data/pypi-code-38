# -*- coding: utf-8 -*-


# 订单评论服务
class UgcService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def get_order_rate_by_order_id(self, order_id):
        """
        获取指定订单的评论
        :param orderId:订单id
        """
        return self.__client.call("eleme.ugc.getOrderRateByOrderId", {"orderId": order_id})

    def get_order_rates_by_order_ids(self, order_ids):
        """
        获取指定订单的评论
        :param orderIds:订单id
        """
        return self.__client.call("eleme.ugc.getOrderRatesByOrderIds", {"orderIds": order_ids})

    def get_unreply_order_rates_by_order_ids(self, order_ids):
        """
        获取未回复的评论
        :param orderIds:订单id
        """
        return self.__client.call("eleme.ugc.getUnreplyOrderRatesByOrderIds", {"orderIds": order_ids})

    def get_order_rates_by_shop_id(self, shop_id, start_time, end_time, offset, page_size):
        """
        获取指定店铺的评论
        :param shopId: 餐厅id
        :param startTime:  开始时间,只能查询最近90天的数据
        :param endTime:  结束时间
        :param offset:页面偏移量
        :param pageSize:页面大小
        """
        return self.__client.call("eleme.ugc.getOrderRatesByShopId", {"shopId": shop_id, "startTime": start_time, "endTime": end_time, "offset": offset, "pageSize": page_size})

    def get_order_rates_by_shop_ids(self, shop_ids, start_time, end_time, offset, page_size):
        """
        获取指定店铺的评论
        :param shopIds:店铺id
        :param startTime:  开始时间,只能查询最近90天的数据
        :param endTime:  结束时间
        :param offset:页面偏移量
        :param pageSize:页面大小
        """
        return self.__client.call("eleme.ugc.getOrderRatesByShopIds", {"shopIds": shop_ids, "startTime": start_time, "endTime": end_time, "offset": offset, "pageSize": page_size})

    def get_unreply_order_rates_by_shop_ids(self, shop_ids, start_time, end_time, offset, page_size):
        """
        获取未回复的评论
        :param shopIds:店铺id
        :param startTime:  开始时间,只能查询最近90天的数据
        :param endTime:  结束时间
        :param offset:页面偏移量
        :param pageSize:页面大小
        """
        return self.__client.call("eleme.ugc.getUnreplyOrderRatesByShopIds", {"shopIds": shop_ids, "startTime": start_time, "endTime": end_time, "offset": offset, "pageSize": page_size})

    def get_order_rates_by_shop_and_rating(self, shop_id, score, start_time, end_time, offset, page_size):
        """
        获取店铺的满意度评价信息
        :param shopId: 餐厅id
        :param score:满意度,取值范围为1~5，1为最不满意，5为非常满意
        :param startTime:  开始时间,只能查询最近90天的数据
        :param endTime:  结束时间
        :param offset:页面偏移量
        :param pageSize:页面大小
        """
        return self.__client.call("eleme.ugc.getOrderRatesByShopAndRating", {"shopId": shop_id, "score": score, "startTime": start_time, "endTime": end_time, "offset": offset, "pageSize": page_size})

    def get_item_rates_by_item_id(self, item_id, start_time, end_time, offset, page_size):
        """
        获取单个商品的评论
        :param itemId: 商品id
        :param startTime:  开始时间,只能查询最近90天的数据
        :param endTime:  结束时间
        :param offset:页面偏移量
        :param pageSize:页面大小
        """
        return self.__client.call("eleme.ugc.getItemRatesByItemId", {"itemId": item_id, "startTime": start_time, "endTime": end_time, "offset": offset, "pageSize": page_size})

    def get_item_rates_by_item_ids(self, item_ids, start_time, end_time, offset, page_size):
        """
        获取多个商品的评论
        :param itemIds:商品id
        :param startTime:  开始时间,只能查询最近90天的数据
        :param endTime:  结束时间
        :param offset:页面偏移量
        :param pageSize:页面大小
        """
        return self.__client.call("eleme.ugc.getItemRatesByItemIds", {"itemIds": item_ids, "startTime": start_time, "endTime": end_time, "offset": offset, "pageSize": page_size})

    def get_unreply_item_rates_by_item_ids(self, item_ids, start_time, end_time, offset, page_size):
        """
        获取多个商品未回复的评论
        :param itemIds:店铺id
        :param startTime:  开始时间,只能查询最近90天的数据
        :param endTime:  结束时间
        :param offset:页面偏移量
        :param pageSize:页面大小
        """
        return self.__client.call("eleme.ugc.getUnreplyItemRatesByItemIds", {"itemIds": item_ids, "startTime": start_time, "endTime": end_time, "offset": offset, "pageSize": page_size})

    def reply_rate_by_order_id(self, order_id, reply):
        """
        回复订单未回复的评论
        :param orderId:订单id
        :param reply:回复内容
        """
        return self.__client.call("eleme.ugc.replyRateByOrderId", {"orderId": order_id, "reply": reply})

    def reply_comment_by_order_ids(self, order_ids, reply):
        """
        批量回复订单未回复的评论
        :param orderIds:订单id
        :param reply:回复信息
        """
        return self.__client.call("eleme.ugc.replyCommentByOrderIds", {"orderIds": order_ids, "reply": reply})

    def reply_rates_by_item_id(self, item_id, reply, start_time, end_time):
        """
        回复商品回复的评论
        :param itemId:商品id
        :param reply:回复内容
        :param startTime:  开始时间,只能查询最近90天的数据
        :param endTime:  结束时间
        """
        return self.__client.call("eleme.ugc.replyRatesByItemId", {"itemId": item_id, "reply": reply, "startTime": start_time, "endTime": end_time})

    def reply_rates_by_item_ids(self, item_ids, reply, start_time, end_time):
        """
        回复多个商品评论
        :param itemIds:商品d
        :param reply:回复信息
        :param startTime:开始时间,只能查询最近90天的数据
        :param endTime:结束时间
        """
        return self.__client.call("eleme.ugc.replyRatesByItemIds", {"itemIds": item_ids, "reply": reply, "startTime": start_time, "endTime": end_time})

    def reply_rate_by_rate_id_and_shop_id(self, rate_id, shop_id, reply_type, reply):
        """
        通过rateId和shopId 回复指定类型的评论(推荐)
        :param rateId:评论编号
        :param shopId: 餐厅id
        :param replyType:评论类型
        :param reply:回复的内容
        """
        return self.__client.call("eleme.ugc.replyRateByRateIdAndShopId", {"rateId": rate_id, "shopId": shop_id, "replyType": reply_type, "reply": reply})

    def reply_rate_by_rate_ids_and_shop_id(self, rate_ids, shop_id, reply_type, reply):
        """
        通过rateIds和shopId 批量回复指定类型的评论(推荐)
        :param rateIds: 评论编号
        :param shopId: 餐厅id
        :param replyType:评论类型
        :param reply:回复的内容
        """
        return self.__client.call("eleme.ugc.replyRateByRateIdsAndShopId", {"rateIds": rate_ids, "shopId": shop_id, "replyType": reply_type, "reply": reply})

    def send_coupon_by_order_id(self, order_id, coupon):
        """
        根据订单ID赠送代金券给该订单的评价用户
        :param orderId: 订单编号
        :param coupon:需要赠送的代金券信息
        """
        return self.__client.call("eleme.ugc.sendCouponByOrderId", {"orderId": order_id, "coupon": coupon})

    def get_order_coupon_status(self, order_id):
        """
        根据订单ID获取该订单评价用户的可赠券状态
        :param orderId: 订单编号
        """
        return self.__client.call("eleme.ugc.getOrderCouponStatus", {"orderId": order_id})

    def get_coupons_by_order_ids(self, order_ids):
        """
        根据订单ID集合获取该订单的已赠券信息集合
        :param orderIds:订单编号集合
        """
        return self.__client.call("eleme.ugc.getCouponsByOrderIds", {"orderIds": order_ids})

    def get_recommend_coupon_by_shop_id(self, shop_id):
        """
        获取店铺的推荐赠送代金券信息
        :param shopId:餐厅ID
        """
        return self.__client.call("eleme.ugc.getRecommendCouponByShopId", {"shopId": shop_id})

    def get_o_rate_result(self, rate_query):
        """
        查询评价信息(推荐)
        :param rateQuery:评价查询参数
        """
        return self.__client.call("eleme.ugc.getORateResult", {"rateQuery": rate_query})

    def count_o_rate_result(self, rate_query):
        """
        统计评价信息数量
        :param rateQuery:评价查询参数
        """
        return self.__client.call("eleme.ugc.countORateResult", {"rateQuery": rate_query})

    def reply_baidu_rate(self, rate_ids, shop_id, reply):
        """
        通过rateIds和shopId 回复饿了么星选评论
        :param rateIds: 评论编号(订单维度)
        :param shopId: 饿了么侧餐厅id
        :param reply:回复的内容
        """
        return self.__client.call("eleme.ugc.replyBaiduRate", {"rateIds": rate_ids, "shopId": shop_id, "reply": reply})

    def send_baidu_coupon(self, rate_id, shop_id, coupon):
        """
        根据rateId和shopId 赠送代金券给该饿了么星选评价对应订单的评价用户
        :param rateId: 评论编号(订单维度)
        :param shopId: 餐厅id
        :param coupon:需要赠送的代金券信息
        """
        return self.__client.call("eleme.ugc.sendBaiduCoupon", {"rateId": rate_id, "shopId": shop_id, "coupon": coupon})

    def get_rate_coupon_status(self, rate_id, shop_id, rate_data_type):
        """
        根据rateId和shopId获取该订单评价用户的可赠券状态(推荐)
        :param rateId: 评论编号(订单维度)
        :param shopId: 餐厅id
        :param rateDataType:评价数据类型
        """
        return self.__client.call("eleme.ugc.getRateCouponStatus", {"rateId": rate_id, "shopId": shop_id, "rateDataType": rate_data_type})

    def rating_coupon(self, rating_coupon_d_t_o):
        """
        根据评价编号赠送代金券给评价用户(推荐)
        :param ratingCouponDTO:赠券所需的参数
        """
        return self.__client.call("eleme.ugc.ratingCoupon", {"ratingCouponDTO": rating_coupon_d_t_o})

    def get_coupon_extends_info(self, extends_queries):
        """
        获取赠券扩展信息(推荐)
        :param extendsQueries:评价赠券信息查询条件
        """
        return self.__client.call("eleme.ugc.getCouponExtendsInfo", {"extendsQueries": extends_queries})

