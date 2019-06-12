# coding=utf-8

from tweb import base_handler, myweb
from tornado import gen
import json
from ..service.async_wrap import ctrl_app


class CustomerOrgHandler(base_handler.BaseHandler):
    """
    开放/关闭客户组（开放客户组后，用户可以主动加入，也即通常的会员功能）
    """

    @myweb.authenticated
    @gen.coroutine
    def post(self, oid, **kwargs):
        employment = self.request.headers.get('x-signed-employment')
        access_token = self.request.headers.get('x-access-token')

        data = json.loads(self.request.body.decode('utf-8'))
        ret = yield ctrl_app.open_customer_org(oid, data, employment, access_token)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def delete(self, oid, **kwargs):
        employment = self.request.headers.get('x-signed-employment')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_app.close_customer_org(oid, employment, access_token)
        return self.write(ret)

