# coding=utf-8

import config
from ..http_handler import entrance_handler as eh

base = '{}/{}/entrance'.format(config.VER, config.PLATFORM)
routes = [
    # 获取工作证列表
    (rf"/{base}/(?P<org>org|com|dept|gov)/(?P<oid>\w+)/employments", eh.QueryEmploymentsHandler),

    # 获取员工所在组的通证列表
    (rf"/{base}/employ/passports", eh.EmployPassportsHandler),

    # 用户加入会员且获取会员组的通证列表
    (rf"/{base}/(?P<org>org|com|dept|gov|app)/(?P<oid>\w+)/member/passports", eh.CustomerPassportsHandler),
]
