# -*- coding: utf-8 -*-


# 门店装修服务
class DecorationService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def create_sign(self, sign):
        """
        创建招贴
        :param sign:招贴信息和其关联门店ID集合
        """
        return self.__client.call("eleme.decoration.sign.createSign", {"sign": sign})

    def update_sign(self, sign_id, sign):
        """
        修改招贴
        :param signId:招贴ID
        :param sign:招贴信息和其关联门店ID
        """
        return self.__client.call("eleme.decoration.sign.updateSign", {"signId": sign_id, "sign": sign})

    def invalid_sign(self, sign_id):
        """
        作废招贴
        :param signId:招贴ID
        """
        return self.__client.call("eleme.decoration.sign.invalidSign", {"signId": sign_id})

    def get_sign_history_image(self, sign):
        """
        获取历史上传过的招贴图片
        :param sign:查询条件
        """
        return self.__client.call("eleme.decoration.sign.getSignHistoryImage", {"sign": sign})

    def query_sign(self):
        """
        查询有效招贴集合
        """
        return self.__client.call("eleme.decoration.sign.querySign", {})

    def get_sign_by_id(self, sign_id):
        """
        根据招贴ID查询店铺招贴详情
        :param signId:招贴ID
        """
        return self.__client.call("eleme.decoration.sign.getSignById", {"signId": sign_id})

    def create_brand_story(self, story):
        """
        新增品牌故事
        :param story:品牌故事信息和其关联连锁店子店ID
        """
        return self.__client.call("eleme.decoration.story.createBrandStory", {"story": story})

    def update_brand_story(self, brand_story_id, story):
        """
        更新品牌故事
        :param brandStoryId:品牌故事ID
        :param story:品牌故事信息和其关联连锁店子店ID
        """
        return self.__client.call("eleme.decoration.story.updateBrandStory", {"brandStoryId": brand_story_id, "story": story})

    def delete_brand_story(self, brand_story_id):
        """
        删除品牌故事
        :param brandStoryId:品牌故事ID
        """
        return self.__client.call("eleme.decoration.story.deleteBrandStory", {"brandStoryId": brand_story_id})

    def query_brand_story_list(self):
        """
        查询品牌故事列表
        """
        return self.__client.call("eleme.decoration.story.queryBrandStoryList", {})

    def get_brand_story_by_id(self, brand_story_id):
        """
        查询当前设置的品牌故事信息
        :param brandStoryId:品牌故事ID
        """
        return self.__client.call("eleme.decoration.story.getBrandStoryById", {"brandStoryId": brand_story_id})

    def save_category(self, category):
        """
        保存精准分类
        :param category:精准分类信息
        """
        return self.__client.call("eleme.decoration.accurateCategory.saveCategory", {"category": category})

    def get_accurate_category(self, category):
        """
        根据门店ID获取精准分类
        :param category:查询参数
        """
        return self.__client.call("eleme.decoration.accurateCategory.getAccurateCategory", {"category": category})

    def query_accurate_category_list(self, category):
        """
        查询精准分类
        :param category:查询参数
        """
        return self.__client.call("eleme.decoration.accurateCategory.queryAccurateCategoryList", {"category": category})

    def create_poster(self, poster):
        """
        创建海报
        :param poster:海报信息和其关联门店ID和门店商品
        """
        return self.__client.call("eleme.decoration.poster.createPoster", {"poster": poster})

    def update_poster(self, poster_id, poster):
        """
        修改海报
        :param posterId:海报ID
        :param poster:海报信息和其关联门店ID和门店商品
        """
        return self.__client.call("eleme.decoration.poster.updatePoster", {"posterId": poster_id, "poster": poster})

    def invalid_poster(self, poster):
        """
        作废海报
        :param poster:作废海报信息
        """
        return self.__client.call("eleme.decoration.poster.invalidPoster", {"poster": poster})

    def get_poster_detail_by_id(self, poster_id):
        """
        根据海报ID获取海报详情
        :param posterId:海报ID
        """
        return self.__client.call("eleme.decoration.poster.getPosterDetailById", {"posterId": poster_id})

    def query_effective_posters(self):
        """
        查询有效的海报信息集合
        """
        return self.__client.call("eleme.decoration.poster.queryEffectivePosters", {})

    def get_poster_history_image(self):
        """
        获取历史上传过的海报图片
        """
        return self.__client.call("eleme.decoration.poster.getPosterHistoryImage", {})

    def save_burst_window(self, burst_window):
        """
        保存爆款橱窗
        :param burstWindow:爆款橱窗信息
        """
        return self.__client.call("eleme.decoration.burstWindow.saveBurstWindow", {"burstWindow": burst_window})

    def close_burst_window_by_shop_id(self, shop_id):
        """
        根据门店ID关闭店铺爆款橱窗
        :param shopId:门店ID
        """
        return self.__client.call("eleme.decoration.burstWindow.closeBurstWindowByShopId", {"shopId": shop_id})

    def get_burst_window_by_shop_id(self, shop_id):
        """
        根据店铺ID查询该店铺的爆款橱窗信息
        :param shopId:店铺ID
        """
        return self.__client.call("eleme.decoration.burstWindow.getBurstWindowByShopId", {"shopId": shop_id})

    def query_burst_window_list(self, shop_ids):
        """
        根据门店ID集合查询店铺爆款橱窗信息集合
        :param shopIds:查询条件
        """
        return self.__client.call("eleme.decoration.burstWindow.queryBurstWindowList", {"shopIds": shop_ids})

    def upload(self, image):
        """
        上传图片
        :param image:文件内容base64编码值
        """
        return self.__client.call("eleme.decoration.image.upload", {"image": image})

    def get_image(self, hash):
        """
        根据图片HASH值获取图片信息
        :param hash:图片HASH值
        """
        return self.__client.call("eleme.decoration.image.getImage", {"hash": hash})

