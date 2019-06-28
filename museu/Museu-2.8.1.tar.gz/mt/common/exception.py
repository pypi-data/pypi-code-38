#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-04-25 14:09:09
# @Author  : Blackstone
# @to      :

class ConfigError(Exception):
	def __init__(self,*msg):
		super(ConfigError,self).__init__("".join(msg))






if __name__=="__main__":
	raise ConfigError("12","23")