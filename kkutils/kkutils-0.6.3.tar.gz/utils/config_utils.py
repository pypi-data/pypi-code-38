#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: zhangkai@cmcm.com
Last modified: 2018-01-05 14:09:42
'''
import os
import re
from configparser import ConfigParser

from .utils import Dict


class Config(object):

    def __init__(self, config):
        self.conf = ConfigParser()
        self.conf.read(config)
        self.config_path = config
        self.options = self.load()

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        elif key in self.options:
            return self.options[key]
        else:
            return None

    __getitem__ = __getattr__

    def load(self):
        options = Dict()
        for section in self.conf.sections():
            if section == "include":
                for key, value in self.conf.items(section):
                    paths = []
                    if os.path.isabs(value):
                        path = value
                    else:
                        path = os.path.join(os.path.dirname(os.path.abspath(self.config_path)), value)

                    if os.path.isdir(path):
                        for filename in os.listdir(path):
                            childpath = os.path.join(os.path.abspath(path), filename)
                            if os.path.isfile(childpath):
                                paths.append(childpath)
                    elif os.path.isfile(path):
                        paths.append(path)

                    options["include"] = paths
                    for path in paths:
                        child = Config(path).options
                        if "include" in child:
                            options["include"] += child["include"]
                            del child["include"]
                        options.update(child)
            else:
                options[section] = Dict()
                for key, value in self.conf.items(section):
                    if re.match(r'^-?[\d]+$', value):
                        options[section][key] = int(value)
                    elif re.match(r'^-?\d+(\.?\d+)?$', value):
                        options[section][key] = float(value)
                    elif re.match(r'^True|False$', value):
                        options[section][key] = eval(value)
                    else:
                        options[section][key] = value
        return options

    def save(self):
        options = self.options
        for section in options.keys():
            if section == "include":
                continue
            if section in self.conf.sections():
                for key, value in options[section].items():
                    self.conf.set(section, key, str(value))
            else:
                new = True
                paths = self.options.get("include", [])
                for path in paths:
                    child = Config(path)
                    # 检查是否在include所包含的配置文件中
                    if section in child.conf.sections():
                        for key, value in options[section].items():
                            child.conf.set(section, key, str(value))
                        child.conf.write(open(path, "w"))
                        new = False
                        break
                if new:
                    self.conf.add_section(section)
                    for key, value in options[section].items():
                        self.conf.set(section, key, str(value))

        self.conf.write(open(self.config_path, "w"))
