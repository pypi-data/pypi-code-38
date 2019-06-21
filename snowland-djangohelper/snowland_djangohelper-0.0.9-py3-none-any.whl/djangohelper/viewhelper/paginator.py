#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: paginator.py
# @time: 2018/8/27 17:56
# @Software: PyCharm
import json
from django.core import serializers
from django.core.paginator import Paginator


def generate_paginator_result(queryset, per_page, orphans=0,
                              allow_empty_first_page=True,
                              length_pagequeue=5, page=1,
                              key_contacts='contacts', key_index='ind'):
    """
    :param queryset: 得到的queryset
    :param per_page: 每一页的条数
    :param orphans:
    :param allow_empty_first_page: 第一页是否可以为空业
    :param length_pagequeue: 显示的页码数量
    :param page: 第几页
    :return:
    """
    if not isinstance(queryset, dict):
        temp_list = json.loads(serializers.serialize('json', queryset))
    else:
        temp_list = queryset
    paginator = Paginator(temp_list, per_page, orphans, allow_empty_first_page)
    contacts = paginator.page(page)
    num_pages = contacts.paginator.num_pages
    if num_pages < length_pagequeue:
        list_show = list(range(1, num_pages + 1))
    elif num_pages - page >= length_pagequeue:
        list_show = list(range(page, page + length_pagequeue))
    else:
        list_show = list(range(num_pages - length_pagequeue + 1, num_pages + 1))

    res_dict = {
        key_contacts: contacts,
        key_index: list_show,
    }
    return res_dict
