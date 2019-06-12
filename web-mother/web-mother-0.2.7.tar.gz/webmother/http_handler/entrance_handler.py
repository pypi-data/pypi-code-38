# coding=utf-8

from tweb import base_handler, myweb
from tornado import gen
from ..service.async_wrap import ctrl_entrance
from ..utils import user_auth


class QueryEmploymentsHandler(base_handler.BaseHandler):
    """
    进入管理圈，获取管理身份
    """

    @myweb.authenticated
    @gen.coroutine
    def get(self, oid, **kwargs):
        uid = self.request.headers.get('x-user-id')
        access_token = self.request.headers.get('x-access-token')

        array, display = yield ctrl_entrance.query_employments(oid, uid, access_token)
        return self.write({'list': array, 'employment_display': display})


class EmployPassportsHandler(base_handler.BaseHandler):
    """
    获取员工的授权列表
    """

    @myweb.authenticated
    @gen.coroutine
    def get(self, **kwargs):
        employment = self.request.headers.get('x-signed-employment')
        access_token = self.request.headers.get('x-access-token')
        system = self.get_argument('sys', 'tree')

        array, display = yield ctrl_entrance.employ_passports(system, employment, access_token)

        return self.write({'list': array, 'passport_display': display})


class CustomerPassportsHandler(base_handler.BaseHandler):
    """
    获取会员的授权列表
    """

    @gen.coroutine
    def get(self, oid, **kwargs):
        uid = self.request.headers.get('x-user-id', None)
        access_token = self.request.headers.get('x-access-token', None)
        auth = yield user_auth.verify(uid, access_token, self.request.remote_ip)

        system = self.get_argument('sys', 'all')
        ret = yield ctrl_entrance.query_customer_passports(system, oid, *auth)

        return self.write(ret)
