# -*- coding: utf-8 -*-
import re
import json
from .api_info import ApiInfo
from ..lib.CommonLogger import debug, info, warn, error
from .api_info_parsers.apidoc import ApiDoc
from .api_info_parsers.cli_doc import CliDoc


class ApiInfoGenerator:
    """
    用于生成需要的对接数据结构
    """

    @classmethod
    def generate_api_info(cls, url, func):
        the_doc = func.__doc__
        if the_doc is None:
            warn("url:{url} func {func} 没有函数doc".format(url=url, func=func))
            return None
        debug("获取url:{url},doc:{doc}".format(url=url, doc=the_doc))
        doc_lines = the_doc.splitlines()
        if len(doc_lines) < 1:
            warn("不支持doc的解析[行数过少]:{d}".format(d=the_doc))
            return None
        else:
            doc_parser = cls.get_doc_parser(doc_lines[0])
            debug("获取到的 doc_parser 是:{func}".format(func=doc_parser))
            the_api_info = doc_parser.parse_doc(doc_lines)
            if the_api_info:
                the_api_info['api'] = func
            else:
                error("生成api [{}],func:{} 信息出错了,doc_parser:{}".format(url, func, doc_parser))
            return the_api_info

    @classmethod
    def get_doc_parser(cls, first_line):
        first_line = first_line.strip().lower()
        debug("检查doc类型:{li}".format(li=first_line))
        match_dict = {
            'att_doc': CliDoc,
            'api_doc': ApiDoc
        }
        return match_dict.get(first_line, CliDoc)
