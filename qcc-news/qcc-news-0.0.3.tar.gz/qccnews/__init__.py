# coding=utf-8

import webmother
from .db import mongo
from . import routes
from .extra_passport import append_extra


def init(app, load_routes=True):
    # 初始化webmother
    webmother.init(app, True)

    # 初始化本系统数据库
    mongo.init()

    # 增加本系统增加的权限需求
    append_extra()

    # 加载路由模块
    if load_routes:
        app.load_routes(routes)


def uninit():
    webmother.uninit()