#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import configparser
from goss.app import utils


class Config():
    def __init__(self, filename=None):
        self.filename = filename

        self.config = configparser.ConfigParser()
        if filename:
            self.config.read(filename)

    def get_value(self, section, name):
        '''获取值'''

        if section not in self.config:
            return None

        sec = self.config[section]

        if name not in sec:
            return None

        return sec[name]


goss_config = Config(utils.GOSS_CONFIG_PATH)

