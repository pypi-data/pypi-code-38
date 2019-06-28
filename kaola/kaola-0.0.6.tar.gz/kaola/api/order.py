from kaola.comm.comm import Comm

ORDER_STATUS = {
    "已付款": 1,
    "已发货": 2,
    "已签收": 3,
    "取消待确认": 5,
    "已取消": 6,
}

SEACH_TYPE = {
    "支付时间": 1,
    "发货时间": 2,
    "签收时间": 3,
    "待发货时间": 1001,
    "取消待处理时间": 1005
}


class Order(Comm):
    """"订单相关API"""

    def search_order(self, order_status, date_type, start_time, end_time, order_id=None, page_no=1, page_size=20):
        """
        订单查询接口
        参数：
        order_status: 订单状态
        date_type: 搜索日期类型
        start_time:开始时间
        end_time:结束时间
        order_id:订单号
        page_no:页码，最大5000
        page_size:每页数量，最大100
        """
        data = {
            "method": "kaola.order.search",
            "order_status": order_status,
            "date_type": date_type,
            "start_time": start_time,
            "end_time": end_time,
            "order_id": order_id,
            "page_no": page_no,
            "page_size": page_size
        }
        return self.post(data=data)

    def get_order(self,order_id):
        """
        获取指定的订单信息
        参数：
        order_id: 订单号
        """
        data = {
            "method": "kaola.order.get",
        }
        return self.post(data=data)