
from kaola.comm.comm import Comm


class Basic(Comm):
    """基础信息"""

    def get_taxnos(self):
        """
        获取所有行邮税号信息
        """
        data = {
            "method": "kaola.common.taxnos.get"
        }
        return self.post(data=data)

    def get_unitcodes(self):
        """
        获取所有度量单位信息
        """
        data = {
            "method": "kaola.common.unitcodes.get"
        }
        return self.post(data=data)

    def get_countries(self):
        """
        获取所有国家信息
        """
        data = {
            "method": "kaola.common.countries.get"
        }
        return self.post(data=data)

    def get_provinces(self):
        """
        获取所有省份信息获取所有省份信息
        """
        data = {
            "method": "kaola.common.provinces.get"
        }
        return self.post(data=data)

    def get_cities(self, province_code):
        """
        获取城市信息
        参数：
        province_code： 省份code
        """
        data = {
            "method": "kaola.common.city.get",
            "province_code": province_code
        }
        return self.post(data=data)

    def get_districts(self, city_code):
        """
        获取区域
        参数：
        city_code： 城市code
        """
        data = {
            "method": "kaola.common.district.get",
            "city_code": city_code
        }
        return self.post(data=data)

    def get_hscodes(self, keyword):
        """
        根据关键字查询hs编码
        """
        data = {
            "keyword": keyword,
            "method": "kaola.common.hscodes.get"
        }
        return self.post(data=data)

    def get_hscodes_by_hsids(self, hs_ids):
        """
        根据hsId查询hs
        参数：
        hs_ids: ids 逗号分隔
        """
        data = {
            "hs_ids": hs_ids,
            "method": "kaola.common.hs.get"
        }
        return self.post(data=data)
