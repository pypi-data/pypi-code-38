#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2018-06-03 00:38:17
'''
import datetime
import hashlib
import random
import uuid

import tornado.web
from utils import Dict

from . import basehandler
from .blueprint import Blueprint

bp = Blueprint('user')


class BaseHandler(basehandler.BaseHandler):

    def encrypt(self, password):
        return hashlib.md5(f'digua_{password}'.encode()).hexdigest()

    def get_user(self, email):
        if email.find('@') >= 0:
            user = self.app.db.users.find_one({'email': email})
        else:
            user = self.app.db.users.find_one({'username': email})
        return user

    def gen_code(self, email):
        code = ''.join(random.sample('0123456789', 4))
        key = f'{self.prefix}_code_{email}'
        self.app.rd.setex(key, 600, code)
        return code

    def check_code(self):
        email = self.get_argument('email', None)
        code = self.get_argument('code', None)
        if email and code:
            key = f'{self.prefix}_code_{email}'
            if code == self.app.rd.get(key):
                return Dict({'err': 0})

        return Dict({'err': 1, 'msg': '验证码无效'})

    def check_username(self):
        username = self.get_argument('username', None)
        if not username:
            return Dict({'err': 1, 'msg': '请输入用户名'})

        if len(username) < 6:
            return Dict({'err': 1, 'msg': '用户名至少6个字符'})

        if len(username) > 20:
            return Dict({'err': 1, 'msg': '用户名至多20个字符'})

        if self.app.db.users.find_one({'username': username}):
            return Dict({'err': 1, 'msg': '用户名重复'})

        return Dict({'err': 0})

    def check_email(self):
        email = self.get_argument('email', None)
        if not email:
            return Dict({'err': 1, 'msg': '请输入Email'})

        if len(email) > 64:
            return Dict({'err': 1, 'msg': 'Email地址太长'})

        if not email.find('@') >= 0:
            return Dict({'err': 1, 'msg': '请填写正确的Email格式'})

        if self.app.db.users.find_one({'email': email}):
            return Dict({'err': 1, 'msg': 'Email地址重复'})

        return Dict({'err': 0})


@bp.route("/check")
class CheckHandler(BaseHandler):

    def get(self):
        for key, value in self.args.items():
            if hasattr(self, f'check_{key}'):
                ret = getattr(self, f'check_{key}')()
                break
        else:
            ret = Dict({'err': 1, 'msg': 'not authorized'})
        self.finish(ret)


@bp.route("/logout")
class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie('user_token')
        self.clear_cookie('user_info')
        self.redirect('/')


@bp.route("/signup")
class SignupHandler(BaseHandler):

    def get(self):
        self.next = self.get_argument('next', '/')
        self.render('signup.html')

    async def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        email = self.get_argument('email', None)
        remember = self.get_argument('remember', None)

        ret = self.check_username()
        if ret.err:
            return self.finish(ret)

        ret = self.check_email()
        if ret.err:
            return self.finish(ret)

        while True:
            token = uuid.uuid4().hex
            if not self.app.db.users.find_one({'token': token}):
                break
        if username and password and email:
            doc = {
                'id': self.app.db.users.seq_id,
                'username': username,
                'password': self.encrypt(password),
                'email': email,
                'token': token,
                'created_at': datetime.datetime.now().replace(microsecond=0)
            }
            self.app.db.users.insert_one(doc)
            if remember == 'on':
                self.set_cookie('user_token', token, expires_days=365)
            else:
                self.set_cookie('user_token', token)
            self.finish({'err': 0, 'msg': '注册成功，激活邮件已发送到您的邮箱'})
            await self.app.http.get(f'https://{self.request.host}/email/active', params={'email': email})
        else:
            self.finish({'err': 1, 'msg': '信息未填写完整'})


@bp.route("/signin")
class SigninHandler(BaseHandler):

    def get(self):
        self.next = self.get_argument('next', '/')
        self.render('signin.html')

    def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        remember = self.get_argument('remember', None)
        if username and password:
            if username.find('@') >= 0:
                doc = {'email': username, 'password': self.encrypt(password)}
            else:
                doc = {'username': username, 'password': self.encrypt(password)}
            user = self.app.db.users.find_one(doc)
            if user:
                ret = {'err': 0, 'msg': '登录成功'}
                if remember == 'on':
                    self.set_cookie('user_token', user.token, expires_days=30)
                else:
                    self.set_cookie('user_token', user.token)
            else:
                ret = {'err': 1, 'msg': '用户名或密码错误'}
        else:
            ret = {'err': 1, 'msg': '请输入用户名和密码'}
        self.finish(ret)


@bp.route("/user")
class UserHandler(BaseHandler):

    def get(self):
        if self.current_user:
            user = dict([(k, v) for k, v in self.current_user.items() if k not in ['token', 'password', '_id']])
            self.finish(user)
        else:
            self.finish({'err': 1, 'msg': '用户未登录'})

    @tornado.web.authenticated
    def post(self):
        old_password = self.get_argument('old_password', None)
        password = self.get_argument('password', None)
        if not (old_password and self.encrypt(old_password) == self.current_user.password):
            return self.finish({'err': 1, 'msg': '原密码错误'})
        if not password:
            return self.finish({'err': 1, 'msg': '请输入新密码'})

        self.app.db.users.update({'_id': self.current_user._id},
                                 {'$set': {'password': self.encrypt(password)}})
        self.finish({'err': 0})


@bp.route("/reset")
class ResetHandler(BaseHandler):

    def get(self):
        self.render('reset.html')

    def post(self):
        ret = self.check_code()
        if ret.err:
            return self.finish(ret)

        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        if email and password:
            user = self.get_user(email)
            if user:
                self.app.db.users.update_one({'_id': user._id},
                                             {'$set': {'password': self.encrypt(password)}})
                self.finish({'err': 0})
            else:
                self.finish({'err': 1, 'msg': '用户不存在'})
        else:
            self.finish({'err': 1, 'msg': '缺少关键信息'})


@bp.route(r'/active/(\w+)')
class ActiveHandler(BaseHandler):

    async def get(self, code):
        email = self.app.rd.get(f'active_{code}')
        if email:
            self.app.db.users.update_one({'email': email}, {'$set': {'active': True}})
        self.redirect('/admin')


@bp.route(r'/email/(\w+)')
class EmailHandler(BaseHandler):

    async def get(self, action):
        email = self.get_argument('email', None)
        if not email:
            return self.finish({'err': 1, 'msg': '请输入邮箱'})

        if action == 'reset':
            user = self.get_user(email)
            if user:
                email = user.email
                title = f'{self.request.host} 重设密码邮件'
                code = self.gen_code(email)
                content = f'您本次操作的验证码为: {code}'
            else:
                return self.finish({'err': 1, 'msg': '用户不存在'})
        elif action == 'active':
            title = f'{self.request.host} 激活邮件'
            code = uuid.uuid4().hex
            self.app.rd.setex(f'active_{code}', 600, email)
            content = f'请点击链接或将其复制到地址栏打开: <br><a href="https://{self.request.host}/active/{code}">https://{self.request.host}/active/{code}</a>'
        else:
            return self.finish({'err': 1, 'msg': 'action is not defined'})

        await self.app.email.send(email, title, content)
        self.finish({'err': 0})

    async def post(self, action):
        await self.get(action)
