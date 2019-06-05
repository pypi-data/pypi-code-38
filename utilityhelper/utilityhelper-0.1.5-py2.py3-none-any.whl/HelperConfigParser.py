#coding:utf-8
'''
Created on 2016年6月24日

@author: Leo
'''
from __future__ import (print_function, unicode_literals)
import os
import sys
from .compatible import *

if PY3:
    from configparser import *
else:
    from ConfigParser import *

class ConfigManager(ConfigParser):
    def __init__(self, cfPath):
        ConfigParser.__init__(self)        
        self._ConfigFile = cfPath
        self.CfgList = self.read(self._ConfigFile)

    def LoadConfig(self):
        pass

    def GetAllSections(self):
        sections = self.sections()
        return sections

    def GetOneOption(self, section, option, craw=False, cvars=None):
        if self.has_option(section, option):
            value = self.get(section, option, craw, cvars)
            return value

    def GetAllOptions(self, section):
        '''获取指定section 的options。即将配置文件某个section 内key 读取到列表中
        '''
        opts = self.options(section)
        return opts

    def SetOneOption(self, section, option, value=None):
        if not self.has_section(section):
            self.add_section(section)
        
        self.set(section, option, value)

    def SetOptions(self, SOVDict):
        '''逐个取出section'''
        for section in SOVDict:
            OVDict = SOVDict[section]
            for option in OVDict:
                value = OVDict[option]
                self.SetOneOption(section, option, value)

    def GetItems(self, section):
        '''把指定section的配置以(key,value)组成的列表返回'''
        if not self.has_section(section):
            return []
        else:
            return self.items(section)

    def SaveConfig(self):
        with open(self._ConfigFile, 'wb') as configfile:
            self.write(configfile)
