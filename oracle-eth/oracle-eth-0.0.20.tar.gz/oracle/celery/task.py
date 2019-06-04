#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
# Author: yuyongpeng@hotmail.com
# Description:
#  

"""
from celery import Celery
import configparser

config = configparser.RawConfigParser()
config.read('/etc/oracle.conf', encoding='utf8')

app = Celery(
    broker="redis://127.0.0.1:6379/1",
    backend="redis://127.0.0.1:6379/1"
)
# app.config_from_object("seting")  # 指定配置文件
app.conf.update(


)

@app.task
def taskA(x,y):
    print('ddddd')
    print('x+y={}+{}'.format(x,y))
    return x + y

@app.task
def taskB(x,y,z):
    print('dfdfdfdfdfd')
    print('x+y+x={}+{}+{}'.format(x,y,z))
    return x + y + z

@app.task
def add(x,y):
    print('ccccccc')
    return x + y