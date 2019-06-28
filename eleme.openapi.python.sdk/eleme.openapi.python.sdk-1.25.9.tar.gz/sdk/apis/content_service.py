# -*- coding: utf-8 -*-
import os
import time
import calendar
from ..efs_client import efsClient

# 视频服务
class ContentService:

    __client = None

    __video_max_size = 200 * 1024 * 1024

    __video_extend_list = ["MP4", "MOV"]

    def __init__(self, client):
        self.__client = client

    def set_video_bind_relation(self, video_id, biz_id, bind_biz_type):
        """
        建立视频与相对应的业务的关联关系
        :param videoId:视频Id
        :param bizId:业务Id(如业务类型为GOOD，业务Id为商品Id)
        :param bindBizType:业务类型
        """
        return self.__client.call("eleme.content.setVideoBindRelation", {"videoId": video_id, "bizId": biz_id, "bindBizType": bind_biz_type})

    def unset_video_bind_relation(self, video_id, biz_id, bind_biz_type):
        """
        取消视频与对应业务的关联关系
        :param videoId:视频Id
        :param bizId:业务Id(如业务类型为GOOD，业务Id为商品Id)
        :param bindBizType:业务类型
        """
        return self.__client.call("eleme.content.unsetVideoBindRelation", {"videoId": video_id, "bizId": biz_id, "bindBizType": bind_biz_type})

    def get_video_info(self, video_id):
        """
        通过视频id查询视频信息
        :param videoId:视频Id
        """
        return self.__client.call("eleme.content.getVideoInfo", {"videoId": video_id})

    def get_video_bind_info(self, video_id):
        """
        通过视频id获取所有相关联的业务关系
        :param videoId:视频Id
        """
        return self.__client.call("eleme.content.getVideoBindInfo", {"videoId": video_id})
