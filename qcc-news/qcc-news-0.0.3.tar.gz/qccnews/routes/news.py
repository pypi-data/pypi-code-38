# coding=utf-8

import config
from ..extra_passport import system_name
from ..http_handler import news_handler, entrance_handler

base = '{}/{}/{}'.format(config.VER, config.PLATFORM, system_name)
base_column = '{}/(?P<fief>fief|tree|node|catalog|column)/(?P<cid>\w+)'.format(base)
routes = [
    # 查询组织拥有哪些资源的许可证/通行证，许可范围有多大
    (rf"/{base}/entrance/employ/passports", entrance_handler.EmployPassportsHandler),

    # 产品的增删改查
    (rf"/{base_column}/news/(?P<news_id>[a-f0-9]*)", news_handler.NewsHandler),

    # 产品的状态操作
    (rf"/{base_column}/news/(?P<news_id>[a-f0-9]*)/do/(?P<action>\w*)", news_handler.StatusHandler),

    # 将产品从一个分类中已到另一分类中
    (rf"/{base_column}/news/(?P<news_id>[a-f0-9]*)/move/(?P<cid_to>\w*)", news_handler.MovingHandler),

    # 查询分类节点下的产品列表
    (rf"/{base_column}/list", news_handler.ListHandler),
]
