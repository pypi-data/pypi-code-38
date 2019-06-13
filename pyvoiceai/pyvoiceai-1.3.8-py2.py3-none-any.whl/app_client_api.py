# -*- coding: utf-8 -*-
from .baseapi import BaseAPI

"""
@author VoiceAI
@desc 本模块是Client API相关
@date 20180928
"""


class AppClientAPI(BaseAPI):
    def __init__(self, base_url, app_id, access_token):
        super(AppClientAPI, self).__init__(base_url, app_id)
        self._access_token = access_token
        self._file_id_list = []

    def app_client_create(self, client_name, describe, group_id, group_name=""):
        """
        创建用户
        :param client_name: 用户名 string
        :param describe:    用户描述 string
        :param group_id:    用户组ID string
        :return:
                成功标志 bool
                用户ID string
        """
        req_json = {
            "access_token": self._access_token,
            "client_name": client_name,
            "describe": describe,
            "groupid": group_id,
            "group_name": group_name
        }
        api_response = self.call_common_api("/api/app/client/create", req_json)
        err = api_response["error"]
        client_id = ""
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]
            client_id = data["clientid"]
        return flag_bool_response, err, client_id

    def app_client_get(self, group_id, group_name="", client_id="", client_name="", page=0, limit=100):
        """
        获取用户
        :param group_id:    用户组ID string
        :param client_id:   用户ID string option
        :return:
            响应数据 object
        """
        req_json = {
            "access_token": self._access_token,
            "groupid": group_id,
            "clientid": client_id,
            "client_name": client_name,
            "group_name": group_name,
            "page": page,
            "limit": limit
        }
        api_response = self.call_common_api("/api/app/client/get", req_json)
        err = api_response["error"]
        data = None
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]

        return flag_bool_response, err, data

    def app_client_delete(self, client_id_list, groupid="", group_name=""):
        """
        删除用户
        :param client_id_list: 用户ID列表 list
        :return:
            响应数据 object
        """
        client_list = []
        for i in range(len(client_id_list)):
            client_list.append({
                "clientid": client_id_list[i]
            })

        req_json = {
            "access_token": self._access_token,
            "client_list": client_list,
            "groupid": groupid,
            "group_name": group_name,
        }
        api_response = self.call_common_api("/api/app/client/delete", req_json)
        err = api_response["error"]
        data = None
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]

        return flag_bool_response, err, data
