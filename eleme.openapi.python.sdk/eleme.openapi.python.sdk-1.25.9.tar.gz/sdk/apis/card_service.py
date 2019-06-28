# -*- coding: utf-8 -*-


# 商户会员卡服务
class CardService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def upload_image(self, image_base_6_4):
        """
        上传图片
        :param imageBase64:上传图片
        """
        return self.__client.call("eleme.card.uploadImage", {"imageBase64": image_base_6_4})

    def create_template(self, template_info):
        """
        创建模板
        :param templateInfo:模板信息
        """
        return self.__client.call("eleme.card.createTemplate", {"templateInfo": template_info})

    def mget_template_info(self, template_id):
        """
        查询模板信息
        :param templateId:模板id列表
        """
        return self.__client.call("eleme.card.mgetTemplateInfo", {"templateId": template_id})

    def update_template(self, template_id, template_info):
        """
        更新模板信息
        :param templateId:模板id
        :param templateInfo:模板更新信息
        """
        return self.__client.call("eleme.card.updateTemplate", {"templateId": template_id, "templateInfo": template_info})

    def mget_shop_ids_by_template_ids(self, template_id):
        """
        查询模板应用的店铺
        :param templateId:模板id列表
        """
        return self.__client.call("eleme.card.mgetShopIdsByTemplateIds", {"templateId": template_id})

    def apply_template(self, template_id, shop_ids):
        """
        应用模板
        :param templateId:模板id
        :param shopIds:店铺列表
        """
        return self.__client.call("eleme.card.applyTemplate", {"templateId": template_id, "shopIds": shop_ids})

    def open_card(self, template_id, card_user_info, card_account_info):
        """
        开卡
        :param templateId:模板ID
        :param cardUserInfo:会员用户信息
        :param cardAccountInfo:会员账户信息
        """
        return self.__client.call("eleme.card.openCard", {"templateId": template_id, "cardUserInfo": card_user_info, "cardAccountInfo": card_account_info})

    def update_user_info(self, card_user_info, card_account_info):
        """
        更新会员信息
        :param cardUserInfo:用户基本信息
        :param cardAccountInfo:用户账户信息
        """
        return self.__client.call("eleme.card.updateUserInfo", {"cardUserInfo": card_user_info, "cardAccountInfo": card_account_info})

    def get_user_by_token(self, user_token):
        """
        根据userToken获取用户信息(该接口不再使用)
        :param userToken:userToken有效期10分钟.饿了么app上跳转到外部H5页面https://www.abc.com?accessToken=c8cea843-1fb5-473f-bb10-a9d2aa239c39,其中accessToken为userToken,用其作为该接口的入参获取到用户信息
        """
        return self.__client.call("eleme.card.getUserByToken", {"userToken": user_token})

    def confirm_send_coupon(self, coupon_request):
        """
        确认是否发券接口
        :param couponRequest:是否发券请求
        """
        return self.__client.call("eleme.card.confirmSendCoupon", {"couponRequest": coupon_request})

