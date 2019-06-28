# -*- coding: utf-8 -*-

# @Date    : 2019-06-27
# @Author  : Peng Shiyu

from __future__ import unicode_literals, print_function
import logging

pure_mysql_logger = logging.getLogger("pure_mysql")
pure_mysql_logger.addHandler(logging.NullHandler())
