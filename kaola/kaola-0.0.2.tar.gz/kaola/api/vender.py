#!/usr/bin/python3
# @Time    : 2019-06-25
# @Author  : Kevin Kong (kfx2007@163.com)

from kaola.comm.comm import Comm


class Vender(Comm):
    """商家类目"""

    def get_vender_categories(self):
        """
        获取商家类目
        """

        data = {
            "method": "kaola.vender.category.get"
        }
        return self.post(data=data)

    def get_vender_brand(self):
        """
        获取商家品牌
        """
        data = {
            "method": "kaola.vender.brand.get"
        }
        return self.post(data=data)

    def get_vender_info(self):
        """
        获取商家基本信息
        """
        data = {
            "method": "kaola.vender.info.get"
        }
        return self.post(data=data)

    def get_vender_warehouses(self):
        """
        获取商家仓库信息
        """
        data = {
            "method": "kaola.vender.warehouse.get"
        }
        return self.post(data=data)
