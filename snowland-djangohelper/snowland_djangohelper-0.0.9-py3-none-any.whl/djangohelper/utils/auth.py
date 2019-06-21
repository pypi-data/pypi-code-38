#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: auth.py
# @time: 2019/3/11 15:21
# @Software: PyCharm

# 代码改自 https://github.com/qiniu/python-sdk/blob/master/qiniu/auth.py
from pysmx.SM2 import *
import time
import json
from urllib.parse import urlparse
from requests.auth import AuthBase
from base64 import b64decode, b64encode, urlsafe_b64decode, urlsafe_b64encode
from djangohelper.number_tool import random_hex_string
class Auth:
    def __init__(self, access_key, secret_key):
        """初始化Auth类"""
        self.__checkKey(access_key, secret_key)
        self.__access_key = access_key
        self.__secret_key = secret_key

    def get_access_key(self):
        return self.__access_key

    def __token(self, data, n:int=32, k=None):
        if k is None:
            assert n
            k = random_hex_string(n)
        signed = Sign(data, self.__secret_key, k, len_para=64)
        return urlsafe_b64encode(signed)

    def token(self, data):
        return '{0}:{1}'.format(self.__access_key, self.__token(data))

    def token_with_data(self, data):
        data = urlsafe_b64encode(data)
        return '{0}:{1}:{2}'.format(
            self.__access_key, self.__token(data), data)

    def token_of_request(self, url, body=None, content_type=None):
        """带请求体的签名（本质上是管理凭证的签名）
        Args:
            url:          待签名请求的url
            body:         待签名请求的body
            content_type: 待签名请求的body的Content-Type
        Returns:
            管理凭证
        """
        parsed_url = urlparse(url)
        query = parsed_url.query
        path = parsed_url.path
        data = path
        if query != '':
            data = ''.join([data, '?', query])
        data = ''.join([data, "\n"])

        if body:
            mimes = [
                'application/x-www-form-urlencoded'
            ]
            if content_type in mimes:
                data += body

        return '{0}:{1}'.format(self.__access_key, self.__token(data))

    @staticmethod
    def __checkKey(access_key, secret_key):
        if not (access_key and secret_key):
            raise ValueError('invalid key')

    def private_download_url(self, url, expires=3600):
        """生成私有资源下载链接
        Args:
            url:     私有空间资源的原始URL
            expires: 下载凭证有效期，默认为3600s
        Returns:
            私有资源的下载链接
        """
        deadline = int(time.time()) + expires
        if '?' in url:
            url += '&'
        else:
            url += '?'
        url = '{0}e={1}'.format(url, str(deadline))

        token = self.token(url)
        return '{0}&token={1}'.format(url, token)

    def upload_token(
            self,
            bucket,
            key=None,
            expires=3600,
            policy=None,
            strict_policy=True):
        """生成上传凭证
        Args:
            bucket:  上传的空间名
            key:     上传的文件名，默认为空
            expires: 上传凭证的过期时间，默认为3600s
            policy:  上传策略，默认为空
        Returns:
            上传凭证
        """
        if bucket is None or bucket == '':
            raise ValueError('invalid bucket name')

        scope = bucket
        if key is not None:
            scope = '{0}:{1}'.format(bucket, key)

        args = dict(
            scope=scope,
            deadline=int(time.time()) + expires,
        )

        if policy is not None:
            self.__copy_policy(policy, args, strict_policy)

        return self.__upload_token(args)

    def __upload_token(self, policy):
        data = json.dumps(policy, separators=(',', ':'))
        return self.token_with_data(data)

    def verify_callback(
            self,
            origin_authorization,
            url,
            body,
            content_type='application/x-www-form-urlencoded'):
        """回调验证
        Args:
            origin_authorization: 回调时请求Header中的Authorization字段
            url:                  回调请求的url
            body:                 回调请求的body
            content_type:         回调请求body的Content-Type
        Returns:
            返回true表示验证成功，返回false表示验证失败
        """
        token = self.token_of_request(url, body, content_type)
        authorization = 'QBox {0}'.format(token)
        return origin_authorization == authorization

    # @staticmethod
    # def __copy_policy(policy, to, strict_policy):
    #     for k, v in policy.items():
    #         if (not strict_policy) or k in _policy_fields:
    #             to[k] = v


class RequestsAuth(AuthBase):
    def __init__(self, auth):
        self.auth = auth

    def __call__(self, r):
        if r.body is not None and r.headers['Content-Type'] == 'application/x-www-form-urlencoded':
            token = self.auth.token_of_request(
                r.url, r.body, 'application/x-www-form-urlencoded')
        else:
            token = self.auth.token_of_request(r.url)
        r.headers['Authorization'] = 'QBox {0}'.format(token)
        return r


class SnowlandMacAuth:
    """
    Sign Requests
    Attributes:
        __access_key
        __secret_key
    """

    def __init__(self, access_key, secret_key):
        self.snowland_header_prefix = "X-Snowland-"
        self.__checkKey(access_key, secret_key)
        self.__access_key = access_key
        self.__secret_key = (secret_key)

    def __token(self, data, n:int=32, k=None):
        if k is None:
            assert n
            k = random_hex_string(n)
        signed = Sign(data, self.__secret_key, k, len_para=64)
        return urlsafe_b64encode(signed)


    def token_of_request(
            self,
            method,
            host,
            url,
            qheaders,
            content_type=None,
            body=None):
        """
        <Method> <PathWithRawQuery>
        Host: <Host>
        Content-Type: <ContentType>
        [<X-Snowland-*> Headers]
        [<Body>] #这里的 <Body> 只有在 <ContentType> 存在且不为 application/octet-stream 时才签进去。
        """
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        path = parsed_url.path
        query = parsed_url.query

        if not host:
            host = netloc

        path_with_query = path
        if query != '':
            path_with_query = ''.join([path_with_query, '?', query])
        data = ''.join(["%s %s" %
                        (method, path_with_query), "\n", "Host: %s" %
                        host, "\n"])

        if content_type:
            data += "Content-Type: %s" % (content_type) + "\n"

        data += qheaders
        data += "\n"

        if content_type and content_type != "application/octet-stream" and body:
            data += body.decode(encoding='UTF-8')

        return '{0}:{1}'.format(self.__access_key, self.__token(data))

    def Snowland_headers(self, headers):
        res = ""
        for key in headers:
            if key.startswith(self.snowland_header_prefix):
                res += key + ": %s\n" % (headers.get(key))
        return res

    @staticmethod
    def __checkKey(access_key, secret_key):
        if not (access_key and secret_key):
            raise ValueError('SnowlandMacAuthSign : Invalid key')


class SnowlandMacRequestsAuth(AuthBase):
    def __init__(self, auth):
        self.auth = auth

    def __call__(self, r):
        token = self.auth.token_of_request(
            r.method, r.headers.get('Host', None),
            r.url, self.auth.snowland_headers(r.headers),
            r.headers.get('Content-Type', None),
            r.body
        )
        r.headers['Authorization'] = 'Snowland {0}'.format(token)
        return r