#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: _tool.py
# @time: 2019/5/29 11:27
# @Software: PyCharm


__author__ = 'A.Star'


def load_install_requires(filepath='requirements.txt', encoding='utf-8'):
    """
    通过filepath生成setup.py的install_requires
    :param filepath:
    :param encoding:
    :return:
    """
    with open(filepath, 'r', encoding=encoding) as f:
        lines = f.readlines()
    return [line.strip() for line in lines if not line.startswith('#')]
