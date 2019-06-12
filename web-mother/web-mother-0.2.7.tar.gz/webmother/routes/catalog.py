# coding=utf-8

import config
from ..http_handler import catalog_handler as h, passport_handler as p

base = '{}/{}/(?P<fief>fief|tree|node|catalog)/(?P<cid>\w+)'.format(config.VER, config.PLATFORM)
routes = [
    # 分类节点的增删改查，增时参数会解析成父节点ID，删改查时则解析成本节点
    (rf"/{base}", h.CatalogHandler),
    # 分类节点的状态操作
    (rf"/{base}/do/(?P<action>\w*)", h.StatusHandler),

    # 查询子节点
    (rf"/{base}/children", h.ChildrenHandler),

    # 移动节点
    (rf"/{base}/move/(?P<cid_to>\w+)", h.MovingHandler),

    # 查询针对分类圈定的资源颁发了哪些许可证，都有些什么权限
    (rf"/{base}/passport/list", p.PassportsHandler),

    # 分类圈定的资源向特定组织的通证（增删改查）
    (rf"/{base}/passport/org/(?P<oid>\w+)", p.PassportHandler),
]
