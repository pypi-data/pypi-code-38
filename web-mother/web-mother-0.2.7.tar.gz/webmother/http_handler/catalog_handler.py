# coding=utf-8

from tweb import base_handler, myweb
from tornado import gen
import json
from ..service.async_wrap import ctrl_catalog
from ..utils import user_auth


class CatalogHandler(base_handler.BaseHandler):
    """
    分类节点基本操作：增删改查（CRUD）
    """

    @myweb.authenticated
    @gen.coroutine
    def post(self, cid, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        data = json.loads(self.request.body.decode('utf-8'))
        ret = yield ctrl_catalog.create(cid, data, passport, access_token)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def get(self, cid, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_catalog.read(cid, passport, access_token)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def put(self, cid, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        data = json.loads(self.request.body.decode('utf-8'))
        ret = yield ctrl_catalog.update(cid, data, passport, access_token)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def delete(self, cid, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_catalog.change_status(cid, 'remove', passport, access_token)
        return self.write(ret)


class StatusHandler(base_handler.BaseHandler):
    """
    节点状态操作，只存在更新操作
    """

    @myweb.authenticated
    @gen.coroutine
    def put(self, cid, action, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_catalog.change_status(cid, action, passport, access_token)
        return self.write(ret)


class ChildrenHandler(base_handler.BaseHandler):
    """
    获取子节点列表
    """

    @gen.coroutine
    def get(self, cid, **kwargs):
        uid = self.request.headers.get('x-user-id')
        access_token = self.request.headers.get('x-access-token')
        passport = self.request.headers.get('x-signed-passport')

        auth = yield user_auth.verify(uid, access_token, self.request.remote_ip)

        ret = yield ctrl_catalog.children(cid, passport, auth[1])
        return self.write({'list': ret})


class MovingHandler(base_handler.BaseHandler):
    """
    节点状态操作，只存在更新操作
    """

    @myweb.authenticated
    @gen.coroutine
    def put(self, cid, cid_to, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_catalog.move(cid, cid_to, passport, access_token)
        return self.write(ret)
