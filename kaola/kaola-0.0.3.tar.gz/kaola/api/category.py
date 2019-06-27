
from kaola.comm.comm import Comm


class Category(Comm):
    """类目"""

    def get_category_attributes(self, category_id):
        """
        获取标准商品类目属性
        """

        data = {
            "method": "kaola.itemprops.get",
            "category_id": category_id
        }

        return self.post(data=data)

    def get_category_values(self, property_value_id):
        """
        获取标准商品类目属性值
        """
        data = {
            "method": "kaola.itempropvalues.get",
            "property_value_id": property_value_id
        }

        return self.post(data=data)
