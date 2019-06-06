# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wjy
import json
import datetime
import traceback
import uuid

import requests
from requests.adapters import HTTPAdapter
from .Models import InsideOutside


def get(url, params: dict = None, header: dict = None, log=None, timeout: int =5, transaction_id: str="",
        is_external: bool = True) -> (int, str):
    """
    兼容http请求和https工具
    :param url: 请求地址
    :param params: url参数
    :param header: 头信息
    :param log: 日志对象
    :param timeout: 超时时间
    :param transaction_id: 流水号， 没有则会自动创建
    :param is_external: 是否记录外部流水
    :return: 返回元组，0是请求成功 响应体，1是请求异常 异常描述
    """
    code, response = 0, ""
    if log:
        log.debug("start url={}, params={}".format(url, params))
    if not transaction_id:
        transaction_id = str(uuid.uuid4()).replace("-", "")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
                             "537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
               "Content-type": "application/json"}
    if header:
        headers.update(header)
    # 创建外部流水日志对西昂
    journal_log = InsideOutside(transaction_id=transaction_id, dialog_type="out", address=url, http_method="GET",
                                key_param=str(params), request_payload=str(params), request_headers=headers)
    # 记录请求前时间
    journal_log.request_time = datetime.datetime.now()
    try:
        request = requests.Session()
        # http请求最多重试3次
        request.mount('http://', HTTPAdapter(max_retries=3))
        # https请求最多重试3次
        request.mount('https://', HTTPAdapter(max_retries=3))
        response = request.get(url=url, params=params, headers=headers, timeout=timeout)
    except requests.exceptions.ConnectTimeout:
        code, response = -1, "调用第三方接口请求超时"
    except requests.exceptions.ReadTimeout:
        code, response = -1, "调用第三方接口响应超时"
    except Exception as e:
        code, response = 1, "接口调用异常url={}, params={}, 异常信息={}".format(url, params, traceback.format_exc())
    else:
        # 设置返回码
        code = response.status_code
        # 记录响应头
        journal_log.response_headers = response.headers
        # 记录响应状态
        journal_log.response_code = response.status_code
        try:
            # 尝试转换json数据
            response = response.json()
        except ValueError:
            # 非json数据
            response = response.content
    finally:
        # 记录响应时间
        journal_log.response_time = datetime.datetime.now()
        # 记录响应数据
        journal_log.response_payload = str(response)
        # 记录请求时差
        jet_lag = (journal_log.response_time - journal_log.request_time).total_seconds()
        # 将请求时间对象转成字符串
        journal_log.request_time = journal_log.request_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        # 将响应时间对西昂转成字符串
        journal_log.response_time = journal_log.response_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        if log:
            if is_external and getattr(log, "external"):
                journal_log.res_content = response
                log.external(msg="end params= {}, response={}=, 响应时间={}".format(params, response, jet_lag),
                             extra=journal_log.__dict__)
            else:
                log.debug("end params= {}, response={}, 响应时间={}".format(params, response, jet_lag))

        return code, {"body": response, "header": journal_log.response_headers}


def post(url, data=None, params: dict = None, header: dict = None, log=None, timeout: int = 5,
         transaction_id: str = "", is_external: bool = True) -> (int, str):
    """
    兼容http请求和https工具
    :param url: 请求地址
    :param data: 请求体数据
    :param params: url参数
    :param header: 头信息
    :param log: 日志对象
    :param timeout: 超时时间
    :param transaction_id: 流水号， 没有则会自动创建
    :param is_external: 是否记录外部流水
    :return: 返回元组，0是请求成功 响应体，1是请求异常 异常描述
    """
    data = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    code, response = 0, ""
    if log:
        log.debug("start url={}, data={}, params={}".format(url, data, params))
    if not transaction_id:
        transaction_id = str(uuid.uuid4()).replace("-", "")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
                             "537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
               "Content-type": "application/json",
               "Content-Length": len(data)}
    if header:
        headers.update(header)
    # 创建外部流水对象
    journal_log = InsideOutside(transaction_id=transaction_id, dialog_type="out", address=url, http_method="POST",
                                key_param=str(data), request_payload=str(data), request_headers=headers)
    # 记录请求前时间
    journal_log.request_time = datetime.datetime.now()
    try:
        request = requests.Session()
        # http请求最多重试3次
        request.mount('http://', HTTPAdapter(max_retries=3))
        # https请求最多重试3次
        request.mount('https://', HTTPAdapter(max_retries=3))
        response = request.post(url=url, data=data, params=params, headers=headers, timeout=timeout)
    except requests.exceptions.ConnectTimeout:
        code, response = -1, "调用第三方接口请求超时"
    except requests.exceptions.ReadTimeout:
        code, response = -1, "调用第三方接口响应超时"
    except Exception as e:
        code, response = 1, "接口调用异常url={}, data={}, params={}, 异常信息={}".format(url, data,
                                                                               params, traceback.format_exc())
    else:
        code = response.status_code
        # 记录响应状态
        journal_log.response_code = response.status_code
        # 记录响应头
        journal_log.response_headers = response.headers
        try:
            # 尝试直接做json转换
            response = response.json()
        except ValueError:
            # 非json响应数据给原始数据
            response = response.content
    finally:
        # 记录响应时间
        journal_log.response_time = datetime.datetime.now()
        # 记录响应数据
        journal_log.response_payload = str(response)
        # 记录请求时差
        jet_lag = (journal_log.response_time - journal_log.request_time).total_seconds()
        # 将请求时间对象转成字符串
        journal_log.request_time = journal_log.request_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        # 将响应时间对西昂转成字符串
        journal_log.response_time = journal_log.response_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        if log:
            if is_external and getattr(log, "external"):
                journal_log.res_content = response
                log.external(msg="end data= {}, response={}, 响应时间={}".format(data, response, jet_lag),
                             extra=journal_log.__dict__)
            else:
                log.debug("end data= {}, response={}, 响应时间={}".format(data, response, jet_lag))
        return code, {"body": response, "header": journal_log.response_headers}
