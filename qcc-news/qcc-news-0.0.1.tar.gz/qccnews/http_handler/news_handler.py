# coding=utf-8

from tweb import base_handler, myweb
from tweb.error_exception import ErrException, ERROR
from tornado import gen
import json
from ..service import ctrl_news
from webmother.utils import user_auth


class NewsHandler(base_handler.BaseHandler):
    """
    新闻文章基本操作：增删改查（CRUD）
    """

    @myweb.authenticated
    @gen.coroutine
    def post(self, cid, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        data = json.loads(self.request.body.decode('utf-8'))
        if 'title' not in data:
            raise ErrException(ERROR.E40000, extra='no title field')

        if 'time' not in data:
            raise ErrException(ERROR.E40000, extra='no time field')

        ret = yield ctrl_news.create(cid, data, passport, access_token)
        return self.write(ret)

    @gen.coroutine
    def get(self, cid, news_id, **kwargs):
        uid = self.request.headers.get('x-user-id')
        access_token = self.request.headers.get('x-access-token')
        passport = self.request.headers.get('x-signed-passport')

        auth = yield user_auth.verify(uid, access_token, self.request.remote_ip)

        ret = yield ctrl_news.read(cid, news_id, passport, auth[1])
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def put(self, cid, news_id, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        data = json.loads(self.request.body.decode('utf-8'))
        ret = yield ctrl_news.update(cid, news_id, data, passport, access_token)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def delete(self, cid, news_id, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_news.change_status(cid, news_id, 'remove', passport, access_token)
        return self.write(ret)


class StatusHandler(base_handler.BaseHandler):
    """
    新闻文章状态操作，只存在更新操作
    """

    @myweb.authenticated
    @gen.coroutine
    def put(self, cid, news_id, action, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_news.change_status(cid, news_id, action, passport, access_token)
        return self.write(ret)


class MovingHandler(base_handler.BaseHandler):
    """
    将新闻文章从一个分类中已到另一分类中
    """

    @myweb.authenticated
    @gen.coroutine
    def put(self, cid, news_id, cid_to, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_news.move(cid, news_id, cid_to, passport, access_token)
        return self.write(ret)


class ListHandler(base_handler.BaseHandler):
    """
    查询目录下的新闻文章列表
    """

    # 读取新闻文章列表为公开接口
    @gen.coroutine
    def get(self, cid, **kwargs):
        uid = self.request.headers.get('x-user-id')
        access_token = self.request.headers.get('x-access-token')
        passport = self.request.headers.get('x-signed-passport')

        page_no = int(self.get_argument('page_no', 1))
        page_size = int(self.get_argument('page_size', 10))

        auth = yield user_auth.verify(uid, access_token, self.request.remote_ip)

        array, total = yield ctrl_news.query_news(cid, page_no, page_size, passport, auth[1])
        return self.write({'total': total, 'list': array})
