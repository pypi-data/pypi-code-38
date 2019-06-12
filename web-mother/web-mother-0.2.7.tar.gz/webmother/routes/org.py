# coding=utf-8

import config
from ..http_handler import org_handler as h, person_handler as person, app_handler

base = '{}/{}/(?P<org>org|com|gov)/(?P<oid>\w+)'.format(config.VER, config.PLATFORM)
routes = [
    # 组织的增删改查
    (rf"/{base}", h.OrgHandler),
    # 组织的状态操作
    (rf"/{base}/do/(?P<action>\w*)", h.StatusHandler),

    # 查询子节点
    (rf"/{base}/children", h.ChildrenHandler),

    # 移动节点
    (rf"/{base}/move/(?P<oid_to>[a-f0-9]*)", h.MovingHandler),

    # 组织人员的增删改查
    (rf"/{base}/person/user/(?P<indicator>[@\\.\w]+)", person.PersonHandler),

    # 获取组织的人员列表
    (rf"/{base}/person/list", person.PersonsHandler),

    # 开放/关闭客户组，以接受客户访问，以及实现对客户的管理，实现会员功能
    (rf"/{base}/customer/entrance", app_handler.CustomerOrgHandler),
]
