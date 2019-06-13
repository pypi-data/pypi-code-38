# -*- coding: utf-8 -*-

from .baseapi import BaseAPI

"""
@author VoiceAI
@desc 本模块是VPR API相关
@date 20180928
"""


class AppVoicePrintAPI(BaseAPI):
    def __init__(self, base_url, app_id, access_token):
        super(AppVoicePrintAPI, self).__init__(base_url, app_id)
        self._access_token = access_token
        self._file_id_list = []

    def get_file_id_list(self):
        """
        获取文件ID列表
        :return: 上次上传文件后的文件标志ID string
        """
        return self._file_id_list

    def app_voiceprint_upload(self, file_path_list, media_type="", sample_rate=""):
        """
        音频文件上传
        :param client_id:       用户ID string
        :param file_path_list:  文件位置列表 list
        :return:
            响应数据 object
        """
        self._file_id_list = []
        req_json = {
            "access_token": self._access_token,
            "media_type": media_type,
            "sample_rate": sample_rate
        }
        files = {}
        for i in range(len(file_path_list)):
            files["file%s" % str(i)] = ("file%s" % str(i), open(file_path_list[i], "rb"))

        api_response = self.call_upload_api("/api/app/voiceprint/upload", req_json, files)
        err = api_response["error"]
        data = None
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]
            file_info_list = data["list"]
            for i in range(len(file_info_list)):
                file_info = file_info_list[i]
                self._file_id_list.append(file_info["fileid"])

        return flag_bool_response, err, data

    def app_voiceprint_register(self, group_id, client_id, src_sample_rate, model_type, file_id_list,
                                group_name="", client_name="", debug=False, debug_data=[]):
        """
        声纹注册
        :param client_id:       客户ID string
        :param group_id:        组ID string
        :param client_name:     客户名字 string  client_id二选一
        :param group_name:      组名字 string   group_id二选一
        :param src_sample_rate: 采样率 int
        :param model_type:      模型类型 string
        :param file_id_list:    文件ID列表 list
        :return:
            响应数据 object
        """
        req_json = {
            "clientid": client_id,
            "src_sample_rate": src_sample_rate,
            "model_type": model_type,
            "access_token": self._access_token,
            "filelist": file_id_list,
            "groupid": group_id,
            "client_name": client_name,
            "group_name": group_name,
            "no_save_file": debug,
            "no_save_file_data": debug_data
        }
        api_response = self.call_common_api("/api/app/voiceprint/register", req_json)
        err = api_response["error"]
        data = None
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]
        return flag_bool_response, err, data

    def app_voiceprint_verify(self, group_id, client_id, src_sample_rate, model_type, file_id_list, get_all_data=True,
                              group_name="", client_name=""):
        """
        声纹验证
        :param group_id:    用户组ID string
        :param client_id:   客户ID string,留空表示1:N
        :param group_name:      组名字 string   group_id二选一
        :param client_name:     客户名字 string  client_id二选一 留空表示1:N
        :param src_sample_rate: 采样率 int
        :param model_type:      模型类型 string
        :param file_id_list:    文件ID列表 list
        :param get_all_data:    是否获取所有信息 bool option
        :return:
            响应数据 object
        """
        req_json = {
            "clientid": client_id,
            "groupid": group_id,
            "src_sample_rate": src_sample_rate,
            "model_type": model_type,
            "access_token": self._access_token,
            "filelist": file_id_list,
            "get_all_data": get_all_data,
            "client_name": client_name,
            "group_name": group_name
        }
        api_response = self.call_common_api("/api/app/voiceprint/verify", req_json)
        err = api_response["error"]
        data = None
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]

        return flag_bool_response, err, data

    def app_voiceprint_asvcheck(self, src_sample_rate, model_type, file_id_list, asv_threshold=None):
        """
        活体检测
        :param src_sample_rate: 采样率 int
        :param model_type:      模型类型 string
        :param file_id_list:    文件ID列表 list
        :param asv_threshold:   unknown
        :return:
            响应数据 object
        """
        req_json = {
            "src_sample_rate": src_sample_rate,
            "model_type": model_type,
            "access_token": self._access_token,
            "filelist": file_id_list,
            "asv_threshold": asv_threshold
        }
        api_response = self.call_common_api("/api/app/voiceprint/asvcheck", req_json)
        err = api_response["error"]
        data = None

        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]

        return flag_bool_response, err, data

    def app_voiceprint_dialaunch(self, group_id, client_id, src_sample_rate, model_type, file_id,
                                 describe="empty des", num_of_speakers_specified=0,
                                 group_name="", client_name=""):
        """
        人声分割
        :param group_id:        用户组ID string
        :param client_id:       客户ID string
        :param client_name:     客户名字 string  client_id二选一
        :param group_name:      组名字 string   group_id二选一
        :param src_sample_rate: 采样率 int
        :param model_type:      模型类型 string
        :param file_id:         文件ID string
        :param describe         描述 string
        :param num_of_speakers_specified unknown optional
        :return:
            响应数据 object
        """
        req_json = {
            "src_sample_rate": src_sample_rate,
            "model_type": model_type,
            "access_token": self._access_token,
            "fileid": file_id,
            "clientid": client_id,
            "groupid": group_id,
            "num_of_speakers_specified": num_of_speakers_specified,
            "describe": describe,
            "client_name": client_name,
            "group_name": group_name
        }
        api_response = self.call_common_api("/api/app/voiceprint/dia", req_json)
        err = api_response["error"]
        task_id = ""
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            task_id = api_response["data"]["task_id"]

        return flag_bool_response, err, task_id

    def app_voiceprint_dia_task_list(self, group_id, client_id, page=0, limit=10, group_name="", client_name=""):
        req_json = {
            "access_token": self._access_token,
            "clientid": client_id,
            "groupid": group_id,
            "page": page,
            "limit": limit,
            "client_name": client_name,
            "group_name": group_name
        }
        api_response = self.call_common_api("/api/app/voiceprint/dia/task", req_json)
        err = api_response["error"]
        data = None
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]

        return flag_bool_response, err, data

    def app_voiceprint_dia_task_list_one(self, group_id, client_id, task_id):
        req_json = {
            "access_token": self._access_token,
            "clientid": client_id,
            "groupid": group_id,
            "task_id": task_id
        }
        api_response = self.call_common_api("/api/app/voiceprint/dia/result", req_json)
        err = api_response["error"]
        data = None
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]

        return flag_bool_response, err, data

    def app_voiceprint_dia_result_download(self, file_id):
        return self.call_download_dia_result_api("/api/app/voiceprint/dia/download", self._access_token, file_id)
