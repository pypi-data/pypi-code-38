# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division, print_function
import datetime
import json
import logging

import requests

# 禁用安全请求警告
try:
    requests.packages.urllib3.disable_warnings()
except:
    pass

"""
@author VoiceAI
@desc 本模块是API基础类
@date 20180928
"""


class BaseAPI(object):
    def __init__(self, base_url, app_id):
        self._base_url = base_url
        self._app_id = app_id
        self.logCallback = callable

    def call_common_api(self, api_path, req_data):
        """
        一般API请求基本接口
        :param api_path:    请求API的URL string
        :param req_data:    请求API的JSON数据 dict
        :return:
            JSON响应数据 object
        """
        logging.debug("call_common_api:%s" % (self._base_url + api_path))
        time_start = datetime.datetime.now()

        full_url = self._base_url + api_path
        base_data = {
            "appid": self._app_id
        }
        final_data = dict(base_data, **req_data)
        logging.debug("request:%s", json.dumps(final_data))
        try:
            r = requests.post(full_url, json=final_data, verify=False)
            logging.debug("response:%r" % r.content)
            rsp_data = r.json()
        except Exception as e:
            rsp_data = {"flag": False, "error": {"errorid": "99999", "errormsg": str(e)}}

        time_end = datetime.datetime.now()
        cost_time = (time_end - time_start).microseconds
        logging.debug("call_common_api 耗时：%f seconds" % (float(cost_time) / 1000000))
        return rsp_data

    def call_upload_api(self, api_path, req_data, files):
        """
        上传文件接口
        :param api_path:    请求API的URL string
        :param req_data:    请求API的JSON数据 dict
        :param files:       上传的文件路径 string
        :return:
            JSON响应数据 object
        """
        logging.debug("call_upload_api:%s" % (self._base_url + api_path))
        time_start = datetime.datetime.now()
        full_url = self._base_url + api_path
        base_data = {
            "appid": self._app_id
        }
        final_data = dict(base_data, **req_data)

        try:
            r = requests.post(full_url, data=final_data, files=files, verify=False)
            logging.debug("response:%r" % r.content)
            rsp_data = r.json()
        except Exception as e:
            rsp_data = {"flag": False, "error": {"errorid": "99999", "errormsg": str(e)}}

        time_end = datetime.datetime.now()
        cost_time = (time_end - time_start).microseconds
        logging.debug("call_upload_api 耗时：%f seconds" % (float(cost_time) / 1000000))
        return rsp_data

    def call_download_dia_result_api(self, api_path, token, file_id):
        """
        临时辅助下载人声分割结果文件
        :param api_path:
        :param file_id:
        :return:
        """
        logging.debug("call_download_dia_result_api:%s" % (self._base_url + api_path))
        time_start = datetime.datetime.now()
        full_url = self._base_url + api_path
        flag = False
        try:
            r = requests.get(full_url, headers={"appid": self._app_id, "access_token": token, "fileid": file_id},
                             verify=False)
            flag = True
            raw_data = r.content
        except Exception as e:
            err = {"flag": False, "error": {"errorid": "99999", "errormsg": str(e)}}

        time_end = datetime.datetime.now()
        cost_time = (time_end - time_start).microseconds
        logging.debug("call_download_dia_result_api 耗时：%f seconds" % (float(cost_time) / 1000000))
        if flag:
            return flag, raw_data
        return flag, err
