# -*- coding: utf-8 -*-


# 签约服务
class PacksService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def get_effect_service_pack_contract(self, shop_id):
        """
        查询店铺当前生效合同类型
        :param shopId:店铺id
        """
        return self.__client.call("eleme.packs.getEffectServicePackContract", {"shopId": shop_id})

