# coding=utf-8

from tweb import base_handler, myweb
from tornado import gen
import json
from ..service.async_wrap import ctrl_passport


class PassportHandler(base_handler.BaseHandler):
    """
    分类向组织的授权(实际上就是操作分类节点与组织之间的关系)
    """

    @myweb.authenticated
    @gen.coroutine
    def post(self, cid, oid, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')
        is_anon = self.get_argument('anon', 0)
        is_anon = int(is_anon)

        try:
            data = json.loads(self.request.body.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            data = None

        ret = yield ctrl_passport.passport_create(cid, oid, data, is_anon, passport, access_token)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def get(self, cid, oid, **kwargs):
        ret = yield ctrl_passport.passport_read(cid, oid)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def put(self, cid, oid, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')
        is_anon = self.get_argument('anon', 0)
        is_anon = int(is_anon)

        data = json.loads(self.request.body.decode('utf-8'))
        ret = yield ctrl_passport.passport_update(cid, oid, data, is_anon, passport, access_token)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def delete(self, cid, oid, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_passport.passport_remove(cid, oid, passport, access_token)
        return self.write(ret)


class PassportsHandler(base_handler.BaseHandler):
    """
    获取分类节点的授权列表
    """

    @myweb.authenticated
    @gen.coroutine
    def get(self, cid, **kwargs):
        array, display = yield ctrl_passport.passports_query(cid)
        return self.write({'list': array, 'passport_display': display})

