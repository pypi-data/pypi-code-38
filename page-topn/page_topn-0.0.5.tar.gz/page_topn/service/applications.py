from tornado.web import Application
from page_topn.service.views.index import IndexHandler
from page_topn.service.configs import settings

"""
用法:
调度
http://10.1.236.151:9000/dispatch?time=now&spider=yyqq188/zjzfcg_bidding_test:latest[&&circle=1d  / 1h]
查看容器和镜像
http://10.1.236.151:9000/dispatch?type=containers /images
"""


class Applications(Application):
    def __init__(self):
        handler = [
            (r"/",IndexHandler),
        ]
        super(Applications,self).__init__(handler,**settings)