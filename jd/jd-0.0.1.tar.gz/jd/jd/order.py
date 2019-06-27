
from jd.comm import Comm


class Order(Comm):

    def get_order_info(self, order_state, optional_fields, order_id):
        """
        输入单个SOP订单id，得到所有相关订单信息
        """
        data = {
            "method": "jingdong.pop.order.get",
            "360buy_param_json": {
                "order_state": order_state,
                "optional_fields": optional_fields,
                "order_id": order_id
            }
        }

        return self.get(data)
