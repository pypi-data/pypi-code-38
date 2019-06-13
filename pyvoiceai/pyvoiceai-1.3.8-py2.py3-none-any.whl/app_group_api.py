# -*- coding: utf-8 -*-
from .baseapi import BaseAPI

"""
@author VoiceAI
@desc 本模块是Group API相关
@date 20180928
"""


class AppGroupAPI(BaseAPI):
    def __init__(self, base_url, app_id, access_token):
        super(AppGroupAPI, self).__init__(base_url, app_id)
        self._access_token = access_token
        self._file_id_list = []

    def app_group_create(self, group_name, describe):
        """
        创建用户组
        :param group_name:  用户组名字 string
        :param describe:    用户组描述 string
        :return:
            用户组ID string
        """
        req_json = {
            "access_token": self._access_token,
            "group_name": group_name,
            "describe": describe
        }
        api_response = self.call_common_api("/api/app/group/create", req_json)
        err = api_response["error"]

        group_id = 0
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]
            group_id = data["groupid"]

        return flag_bool_response, err, group_id

    def app_group_get(self, group_id="", group_name=""):
        """
        获取用户组
        :param group_id:    用户组ID
        :return:
            响应数据 object
        """
        req_json = {
            "access_token": self._access_token,
            "groupid": group_id,
            "group_name": group_name
        }
        api_response = self.call_common_api("/api/app/group/get", req_json)
        err = api_response["error"]
        data = None
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]
        return flag_bool_response, err, data

    def app_group_delete(self, group_id_list):
        """
        删除用户组
        :param group_id_list:   用户组ID列表
        :return:
            响应数据 object
        """
        group_list = []
        for i in range(len(group_id_list)):
            group_list.append({
                "groupid": group_id_list[i]
            })

        req_json = {
            "access_token": self._access_token,
            "group_list": group_list
        }
        api_response = self.call_common_api("/api/app/group/delete", req_json)
        err = api_response["error"]
        data = None

        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]
        return flag_bool_response, err, data

    def app_group_count_client(self, group_id, group_name):
        """
        获取用户组下用户数
        :param group_id:   用户组ID string
        :param group_name:   用户组名字 string
        :return:
            响应数据 object
        """
        req_json = {
            "access_token": self._access_token,
            "group_id": group_id,
            "group_name": group_name
        }
        api_response = self.call_common_api("/api/app/group/clientcount", req_json)
        err = api_response["error"]
        data = None

        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]
        return flag_bool_response, err, data
