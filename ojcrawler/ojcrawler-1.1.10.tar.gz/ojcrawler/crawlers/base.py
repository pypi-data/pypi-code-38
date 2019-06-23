# -*- coding: utf-8 -*-
# Created by crazyX on 2018/7/8
from socket import timeout
from urllib.error import URLError, HTTPError
from ojcrawler.crawlers.config import logger
from ojcrawler.crawlers.config import HTTP_METHOD_TIMEOUT


class OJ(object):
    # 每一个账号同一时间只考虑交一道题目，这样可以有效避免查封，且方便处理
    # image_func 用来做网页中图片的url替换
    def __init__(self, handle, password, image_func):
        self.handle = handle
        self.password = password
        self.image_func = image_func

    def __str__(self):
        return "{}({})".format(self.oj_name, self.handle)

    @property
    def oj_name(self):
        return self.__class__.__name__.lower()

    # 以下为基础属性
    @property
    def browser(self):
        raise NotImplementedError

    @property
    def url_home(self):
        raise NotImplementedError

    def url_problem(self, *args, **kwargs):
        raise NotImplementedError

    @property
    def url_login(self):
        raise NotImplementedError

    @property
    def url_submit(self):
        raise NotImplementedError

    @property
    def url_status(self):
        raise NotImplementedError

    @property
    def http_headers(self):
        raise NotImplementedError

    @property
    def uncertain_result_status(self):
        raise NotImplementedError

    @property
    def compatible_problem_fields(self):
        # title 为标题，字符串
        # time limit 数字，单位为 ms
        # memory limit 数字，单位为 kb
        # problem_type为字符串，表示题目类型，默认为'regular', 可选为'special judge'，'interactive'等
        # origin 为题目链接字符串

        # samples_input\output为list：
        # 注意某些samples可能没有输入或者没有输出

        # descriptions为所有描述，hint, source, 等内容的二元组有序列表，内容都为html源码，并替换了其中的image路径为本地路径
        # [(sub_title1, html1), (sub_title2, html2), ...]

        # 需要额外考虑一下针对不同语言的不同的time limit和memory limit
        # time_limit = {
        #   'default': 1000,
        #   'java': 3000,
        # }
        # memory_limit = {
        #   'default': 65536,
        # }

        # Description, Input, Output, Samples, Hint, Source,

        # 增加两个字段，一个是category，一个是tags
        # 对于poj，将其source的text转为category；tags初始空，后期手动标注；
        # 对于hdu，将其source的text转为category；tags初始空，后期手动标注；
        # 对于codeforces，将其对应比赛名转为category；tags为problem tags；

        # category默认为空字符串，且每个题目最多对应到一个确定的category
        # 每个题目可以对应到多个tag, tags类型为list

        # 增加一个append_html项，可能有依赖的html样式或者mathjax配置等等

        return ['title', 'problem_type', 'origin',
                'limits',
                'samples',
                # 'time_limit', 'memory_limit',
                # 'samples_input', 'samples_output',
                'descriptions',
                'category',
                'tags',
                'append_html',
                ]

    # 以下为基础函数
    def get(self, url):
        try:
            return self.browser.open(url, timeout=HTTP_METHOD_TIMEOUT)
        except (HTTPError, URLError) as error:
            logger.error('Data not retrieved because %s\nURL: %s', error, url)
            return None
        except timeout:
            logger.error('socket timed out\nURL: %s', url)
            return None

    def post(self, url, data):
        raise NotImplementedError

    @staticmethod
    def http_status_code(response):
        return response.status if response else None

    def ping(self):
        # 5s是否能访问主页
        response = self.get(self.url_home)
        return self.http_status_code(response) == 200

    @staticmethod
    def get_languages():
        # 获取语言列表
        # example:
        # LANGUAGE = {
        #     'G++': '1',
        #     'G++11': '42',
        #     'G++14': '50',
        #     'GCC': '10',
        #     'JAVA': '36',
        #     'PYTHON2': '7',
        #     'PYTHON3': '31',
        # }
        raise NotImplementedError

    def login(self):
        raise NotImplementedError

    def is_login(self):
        raise NotImplementedError

    def replace_image(self, html):
        raise NotImplementedError

    def get_problem(self, *args, **kwargs):
        raise NotImplementedError

    def submit_code(self, *args, **kwargs):
        # 返回 run id
        raise NotImplementedError

    def get_result(self):
        # 只需要获取最近一次提交的结果
        # 如果遇到了什么异常，考虑直接重新提交
        raise NotImplementedError

    def get_result_by_rid(self, rid):
        # 这个不一定每个系统都能实现
        pass

    def get_compile_error_info(self, rid):
        # 这个不一定每个系统都能实现
        pass
