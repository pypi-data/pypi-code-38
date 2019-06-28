# -*- coding: utf-8 -*-


# 订单服务
class OrderService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def get_delivery_routes(self, order_id):
        """
        获取订单配送轨迹
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.delivery.getDeliveryRoutes", {"orderId": order_id})

    def get_order(self, order_id):
        """
        获取订单
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.getOrder", {"orderId": order_id})

    def mget_orders(self, order_ids):
        """
        批量获取订单
        :param orderIds:订单Id的列表
        """
        return self.__client.call("eleme.order.mgetOrders", {"orderIds": order_ids})

    def confirm_order_lite(self, order_id):
        """
        确认订单(推荐)
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.confirmOrderLite", {"orderId": order_id})

    def cancel_order_lite(self, order_id, type, remark):
        """
        取消订单(推荐)
        :param orderId:订单Id
        :param type:取消原因
        :param remark:备注说明
        """
        return self.__client.call("eleme.order.cancelOrderLite", {"orderId": order_id, "type": type, "remark": remark})

    def agree_refund_lite(self, order_id):
        """
        同意退单/同意取消单(推荐)
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.agreeRefundLite", {"orderId": order_id})

    def disagree_refund_lite(self, order_id, reason):
        """
        不同意退单/不同意取消单(推荐)
        :param orderId:订单Id
        :param reason:商家不同意退单原因
        """
        return self.__client.call("eleme.order.disagreeRefundLite", {"orderId": order_id, "reason": reason})

    def get_delivery_state_record(self, order_id):
        """
        获取订单配送记录
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.getDeliveryStateRecord", {"orderId": order_id})

    def batch_get_delivery_states(self, order_ids):
        """
        批量获取订单最新配送记录
        :param orderIds:订单Id列表
        """
        return self.__client.call("eleme.order.batchGetDeliveryStates", {"orderIds": order_ids})

    def delivery_by_self_lite(self, order_id):
        """
        配送异常或者物流拒单后选择自行配送(推荐)
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.deliveryBySelfLite", {"orderId": order_id})

    def no_more_delivery_lite(self, order_id):
        """
        配送异常或者物流拒单后选择不再配送(推荐)
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.noMoreDeliveryLite", {"orderId": order_id})

    def received_order_lite(self, order_id):
        """
        订单确认送达
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.receivedOrderLite", {"orderId": order_id})

    def start_delivery_by_self(self, order_id, phone):
        """
        订单确认送出(自配送)
        :param orderId:订单Id
        :param phone:配送者电话
        """
        return self.__client.call("eleme.order.startDeliveryBySelf", {"orderId": order_id, "phone": phone})

    def complete_delivery_by_self(self, order_id, phone):
        """
        订单确认送达(自配送)
        :param orderId:订单Id
        :param phone:配送者电话
        """
        return self.__client.call("eleme.order.completeDeliveryBySelf", {"orderId": order_id, "phone": phone})

    def reply_reminder(self, remind_id, type, content):
        """
        回复催单
        :param remindId:催单Id
        :param type:回复类别
        :param content:回复内容,如果type为custom,content必填,回复内容不能超过30个字符
        """
        return self.__client.call("eleme.order.replyReminder", {"remindId": remind_id, "type": type, "content": content})

    def get_commodities(self, order_id):
        """
        获取指定订单菜品活动价格.
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.getCommodities", {"orderId": order_id})

    def mget_commodities(self, order_ids):
        """
        批量获取订单菜品活动价格
        :param orderIds:订单Id列表
        """
        return self.__client.call("eleme.order.mgetCommodities", {"orderIds": order_ids})

    def get_refund_order(self, order_id):
        """
        获取订单退款信息
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.getRefundOrder", {"orderId": order_id})

    def mget_refund_orders(self, order_ids):
        """
        批量获取订单退款信息
        :param orderIds:订单Id列表
        """
        return self.__client.call("eleme.order.mgetRefundOrders", {"orderIds": order_ids})

    def cancel_delivery(self, order_id):
        """
        取消呼叫配送
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.cancelDelivery", {"orderId": order_id})

    def call_delivery(self, order_id, fee):
        """
        呼叫配送
        :param orderId:订单Id
        :param fee:小费,1-8之间的整数
        """
        return self.__client.call("eleme.order.callDelivery", {"orderId": order_id, "fee": fee})

    def get_unreply_reminders(self, shop_id):
        """
        获取店铺未回复的催单
        :param shopId:店铺Id
        """
        return self.__client.call("eleme.order.getUnreplyReminders", {"shopId": shop_id})

    def get_unprocess_orders(self, shop_id):
        """
        查询店铺未处理订单
        :param shopId:店铺Id
        """
        return self.__client.call("eleme.order.getUnprocessOrders", {"shopId": shop_id})

    def get_cancel_orders(self, shop_id):
        """
        查询店铺未处理的取消单
        :param shopId:店铺Id
        """
        return self.__client.call("eleme.order.getCancelOrders", {"shopId": shop_id})

    def get_refund_orders(self, shop_id):
        """
        查询店铺未处理的退单
        :param shopId:店铺Id
        """
        return self.__client.call("eleme.order.getRefundOrders", {"shopId": shop_id})

    def get_all_orders(self, shop_id, page_no, page_size, date):
        """
        查询全部订单
        :param shopId:店铺Id
        :param pageNo:页码。取值范围:大于零的整数最大限制为100
        :param pageSize:每页获取条数。最小值1，最大值50。
        :param date:日期,默认当天,格式:yyyy-MM-dd
        """
        return self.__client.call("eleme.order.getAllOrders", {"shopId": shop_id, "pageNo": page_no, "pageSize": page_size, "date": date})

    def query_supported_compensation_orders(self, order_ids):
        """
        批量查询订单是否支持索赔
        :param orderIds:索赔订单Id的列表
        """
        return self.__client.call("eleme.order.querySupportedCompensationOrders", {"orderIds": order_ids})

    def batch_apply_compensations(self, requests):
        """
        批量申请索赔
        :param requests:索赔请求的列表
        """
        return self.__client.call("eleme.order.batchApplyCompensations", {"requests": requests})

    def query_compensation_orders(self, order_ids):
        """
        批量查询索赔结果
        :param orderIds:索赔订单Id的列表
        """
        return self.__client.call("eleme.order.queryCompensationOrders", {"orderIds": order_ids})

    def get_delivery_fee_for_crowd(self, order_id):
        """
        众包订单询价，获取配送费
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.getDeliveryFeeForCrowd", {"orderId": order_id})

    def evaluate_rider(self, order_id, evaluation_info):
        """
        评价骑手
        :param orderId:订单Id
        :param evaluationInfo:评价信息
        """
        return self.__client.call("eleme.order.evaluateRider", {"orderId": order_id, "evaluationInfo": evaluation_info})

    def mget_evaluation_infos(self, order_ids):
        """
        批量获取骑手评价信息
        :param orderIds:订单Id的列表
        """
        return self.__client.call("eleme.order.mgetEvaluationInfos", {"orderIds": order_ids})

    def mget_evaluation_status(self, order_ids):
        """
        批量获取是否可以评价骑手
        :param orderIds:订单Id的列表
        """
        return self.__client.call("eleme.order.mgetEvaluationStatus", {"orderIds": order_ids})

    def mget_delivery_tip_infos(self, order_ids):
        """
        批量获取订单加小费信息
        :param orderIds:订单Id的列表
        """
        return self.__client.call("eleme.order.mgetDeliveryTipInfos", {"orderIds": order_ids})

    def add_delivery_tip_by_order_id(self, order_id, tip):
        """
        订单加小费
        :param orderId:订单Id
        :param tip:小费金额
        """
        return self.__client.call("eleme.order.addDeliveryTipByOrderId", {"orderId": order_id, "tip": tip})

    def apply_refund(self, order_id, type, remark):
        """
        主动发起退单
        :param orderId:订单Id
        :param type:取消原因
        :param remark:备注说明
        """
        return self.__client.call("eleme.order.applyRefund", {"orderId": order_id, "type": type, "remark": remark})

    def set_order_prepared(self, order_id):
        """
        非自配送餐厅标记已出餐
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.setOrderPrepared", {"orderId": order_id})

    def get_prepared_times_by_order_ids(self, order_ids):
        """
        查询已出餐列表
        :param orderIds:查询已出餐订单Id的列表
        """
        return self.__client.call("eleme.order.getPreparedTimesByOrderIds", {"orderIds": order_ids})

    def mget_user_simple_info_by_order_ids(self, order_ids):
        """
        查询顾客联系方式
        :param orderIds:订单Id的列表
        """
        return self.__client.call("eleme.order.mgetUserSimpleInfoByOrderIds", {"orderIds": order_ids})

    def refund_part(self, order_id, refund_order_message):
        """
        商家部分退款
        :param orderId:订单Id
        :param refundOrderMessage:退款详情
        """
        return self.__client.call("eleme.order.refundPart", {"orderId": order_id, "refundOrderMessage": refund_order_message})

    def set_invoice_url(self, order_id, invoice_url):
        """
        设置订单开票地址
        :param orderId:订单Id
        :param invoiceUrl:开票地址
        """
        return self.__client.call("eleme.order.setInvoiceUrl", {"orderId": order_id, "invoiceUrl": invoice_url})

    def self_delivery_state_sync(self, shop_id, state_info):
        """
        自配送商家同步运单的状态信息
        :param shopId:店铺Id
        :param stateInfo:运单状态信息
        """
        return self.__client.call("eleme.order.selfDeliveryStateSync", {"shopId": shop_id, "stateInfo": state_info})

    def self_delivery_location_sync(self, shop_id, order_id, location_info):
        """
        自配送商家同步运单的位置信息
        :param shopId:店铺Id
        :param orderId:订单Id
        :param locationInfo:位置信息,仅接受火星坐标系
        """
        return self.__client.call("eleme.order.selfDeliveryLocationSync", {"shopId": shop_id, "orderId": order_id, "locationInfo": location_info})

    def order_predict_finish_time(self, order_id, predict_time):
        """
        订单预计出餐时间
        :param orderId:订单Id
        :param predictTime:预计订单出餐时间
        """
        return self.__client.call("eleme.order.orderPredictFinishTime", {"orderId": order_id, "predictTime": predict_time})

    def commodity_predict_finish_time(self, shop_id, commodity_info):
        """
        菜品预计出餐时间
        :param shopId:店铺Id
        :param commodityInfo:菜品信息
        """
        return self.__client.call("eleme.order.commodityPredictFinishTime", {"shopId": shop_id, "commodityInfo": commodity_info})

    def commodity_actual_finish_time(self, shop_id, commodity_info):
        """
        菜品实际出餐时间
        :param shopId:店铺Id
        :param commodityInfo:菜品信息
        """
        return self.__client.call("eleme.order.commodityActualFinishTime", {"shopId": shop_id, "commodityInfo": commodity_info})

    def query_call_available(self, order_id):
        """
        匿名订单查询可用虚拟小号
        :param orderId:订单Id
        """
        return self.__client.call("eleme.order.queryCallAvailable", {"orderId": order_id})

