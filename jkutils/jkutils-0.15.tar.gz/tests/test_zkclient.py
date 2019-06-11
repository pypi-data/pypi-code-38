#!/usr/bin/env python

#-*-coding:utf-8-*-

"""
@author: vcancy
@software: PyCharm
@file: test_zkclient.py
@time: 2019/6/10 3:24 PM
@description:
"""
from jkutils.zkCli import ConfigZKClient,RegisterZkClient

def test_configzk():
    zk = ConfigZKClient("127.0.0.1:2181","test","/entry/config/service",)
    print(zk.server_config_path)
    zk.read_config()
    assert zk.config=={} and zk.zk_node_number

def test_registerzk():
    zk = RegisterZkClient("127.0.0.1:2181","127.0.0.1:8080","/entry/service/","test")
    zk.register()