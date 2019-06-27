
from kaola.comm.comm import Comm


class Deliery(Comm):

    def delivery(self, order_id, express_company_code, express_no, sku_info=None):
        """
        发货通知
        参数：
        order_id: 订单ID
        express_company_code: 快递公司代码
        express_no: 快递单号
        sku_info: sku
        """
        data = {
            "method": "kaola.logistics.deliver",
            "order_id": order_id,
            "express_company_code": express_company_code,
            "express_no": express_no,
            "sku_info": sku_info
        }

        return self.post(data=data)

    def add_package(self, order_id, express_company_code, express_no):
        """
        此接口是用于实现追加包裹功能，如果订单未发货，调用此接口为发货，第二次调用则相当于此订单追加的包裹
        """
        data = {
            "method": "kaola.logistics.package.add",
            "order_id": order_id,
            "express_company_code": express_company_code,
            "express_no": express_no,
        }

        return self.post(data=data)

    def get_express_company(self):
        """
        获取快递公司信息
        """
        data = {
            "method": "kaola.logistics.companies.get"
        }
        return self.post(data=data)
