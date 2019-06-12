# coding=utf-8

from tweb import base_handler, myweb
from tornado import gen
import json
from ..service.async_wrap import ctrl_org


class OrgHandler(base_handler.BaseHandler):
    """
    分类节点基本操作：增删改查（CRUD）
    """

    @myweb.authenticated
    @gen.coroutine
    def post(self, oid, **kwargs):
        employment = self.request.headers.get('x-signed-employment')
        access_token = self.request.headers.get('x-access-token')

        data = json.loads(self.request.body.decode('utf-8'))
        ret = yield ctrl_org.create(oid, data, employment, access_token)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def get(self, oid, **kwargs):
        employment = self.request.headers.get('x-signed-employment')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_org.read(oid, employment, access_token)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def put(self, oid, **kwargs):
        employment = self.request.headers.get('x-signed-employment')
        access_token = self.request.headers.get('x-access-token')

        data = json.loads(self.request.body.decode('utf-8'))
        ret = yield ctrl_org.update(oid, data, employment, access_token)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def delete(self, oid, **kwargs):
        employment = self.request.headers.get('x-signed-employment')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_org.change_status(oid, 'remove', employment, access_token)
        return self.write(ret)


class StatusHandler(base_handler.BaseHandler):
    """
    节点状态操作，只存在更新操作
    """

    @myweb.authenticated
    @gen.coroutine
    def put(self, oid, action, **kwargs):
        employment = self.request.headers.get('x-signed-employment')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_org.change_status(oid, action, employment, access_token)
        return self.write(ret)


class ChildrenHandler(base_handler.BaseHandler):
    """
    获取子节点列表
    """

    @myweb.authenticated
    @gen.coroutine
    def get(self, oid, **kwargs):
        employment = self.request.headers.get('x-signed-employment')
        access_token = self.request.headers.get('x-access-token')

        array = yield ctrl_org.children(oid, employment, access_token)
        return self.write({'list': array})


class MovingHandler(base_handler.BaseHandler):
    """
    节点状态操作，只存在更新操作
    """

    @myweb.authenticated
    @gen.coroutine
    def put(self, oid, oid_to, **kwargs):
        employment = self.request.headers.get('x-signed-employment')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_org.move(oid, oid_to, employment, access_token)
        return self.write(ret)

