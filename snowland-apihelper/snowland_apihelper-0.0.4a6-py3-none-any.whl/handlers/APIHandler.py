#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: APIHandler.py
# @time: 2019/1/11 10:43
# @Software: PyCharm

import base64
import datetime
import hmac
import json
import time
from abc import abstractmethod
from jsonschema import ValidationError
from pysmx.crypto.hashlib import sm3
from snowland_authsdk.util import random_string
from tornado.escape import utf8
from tornado.web import _get_version  # , _time_independent_equals
from tornado.web import authenticated
from tornado.web import create_signed_value as tornado_create_signed_value
from tornado.web import decode_signed_value as tornado_decode_signed_value

from apihelper.database.models import AbstractUser, User, Session, AbstractSession
from apihelper.database.models import generate_session_data
from apihelper.thirdparty.tornado_json.exceptions import APIError
from apihelper.thirdparty.tornado_json.requesthandlers import BaseHandler as Base
from apihelper.util.jsend import JSendMixin
from apihelper.common import *


def _create_signature_v3(secret, s):
    hash = hmac.new(utf8(secret), digestmod=sm3)
    hash.update(utf8(s))
    return utf8(hash.hexdigest())


def create_signed_value(secret, name, value, version=None, clock=None,
                        key_version=None):
    if version is None:
        version = DEFAULT_SIGNED_VALUE_VERSION
    if clock is None:
        clock = time.time

    timestamp = utf8(str(int(clock())))
    value = base64.b64encode(utf8(value))
    if version < 3:
        return tornado_create_signed_value(secret, name, value, version, clock,
                                           key_version)
    elif version == 3:
        def format_field(s):
            return utf8("%d:" % len(s)) + utf8(s)

        to_sign = b"|".join([
            b"3",
            format_field(str(key_version or 0)),
            format_field(timestamp),
            format_field(name),
            format_field(value),
            b''])

        if isinstance(secret, dict):
            assert key_version is not None, 'Key version must be set when sign key dict is used'
            assert version >= 2, 'Version must be at least 2 for key version support'
            secret = secret[key_version]

        signature = _create_signature_v3(secret, to_sign)
        return to_sign + signature
    else:
        raise ValueError("Unsupported version %d" % version)


def _decode_fields_v3(value):
    def _consume_field(s):
        length, _, rest = s.partition(b':')
        n = int(length)
        field_value = rest[:n]
        # In python 3, indexing bytes returns small integers; we must
        # use a slice to get a byte string as in python 2.
        if rest[n:n + 1] != b'|':
            raise ValueError("malformed v3 signed value field")
        rest = rest[n + 1:]
        return field_value, rest

    rest = value[2:]  # remove version number
    key_version, rest = _consume_field(rest)
    timestamp, rest = _consume_field(rest)
    name_field, rest = _consume_field(rest)
    value_field, passed_sig = _consume_field(rest)
    return int(key_version), timestamp, name_field, value_field, passed_sig


def _decode_signed_value_v3(secret, name, value, max_age_days, clock):
    try:
        key_version, timestamp_bytes, name_field, value_field, passed_sig = _decode_fields_v3(
            value
        )
    except ValueError:
        return None
    signed_string = value[: -len(passed_sig)]

    if isinstance(secret, dict):
        try:
            secret = secret[key_version]
        except KeyError:
            return None

    expected_sig = _create_signature_v3(secret, signed_string)
    if not hmac.compare_digest(passed_sig, expected_sig):
        return None
    if name_field != utf8(name):
        return None
    timestamp = int(timestamp_bytes)
    if timestamp < clock() - max_age_days * 86400:
        # The signature has expired.
        return None
    try:
        return base64.b64decode(value_field)
    except Exception as e:
        return None


def decode_signed_value(secret, name, value, max_age_days=31,
                        clock=None, min_version=None):
    if clock is None:
        clock = time.time
    if min_version is None:
        min_version = DEFAULT_SIGNED_VALUE_MIN_VERSION
    if min_version > 3:
        raise ValueError("Unsupported min_version %d" % min_version)
    if not value:
        return None

    value = utf8(value)
    version = _get_version(value)

    if version < min_version:
        return None
    if version == 1 or version == 2:
        tornado_decode_signed_value(secret, name, value,
                                    max_age_days, clock)
    elif version == 3:
        return _decode_signed_value_v3(secret, name, value,
                                       max_age_days, clock)
    else:
        return None


class BaseHandler(Base):
    """解决JS跨域请求问题"""
    cookie_name = 'apihelper_session'
    user_model = User
    session_model = Session

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def create_signed_value(self, name, value, version=3):
        """Signs and timestamps a string so it cannot be forged.

        Normally used via set_secure_cookie, but provided as a separate
        method for non-cookie uses.  To decode a value not stored
        as a cookie use the optional value argument to get_secure_cookie.

        .. versionchanged:: 3.2.1

           Added the ``version`` argument.  Introduced cookie version 2
           and made it the default.
        """
        self.require_setting("cookie_secret", "secure cookies")
        secret = self.application.settings["cookie_secret"]
        key_version = None
        if isinstance(secret, dict):
            if self.application.settings.get("key_version") is None:
                raise Exception("key_version setting must be used for secret_key dicts")
            key_version = self.application.settings["key_version"]

        return create_signed_value(secret, name, value, version=version,
                                   key_version=key_version)

    def set_secure_cookie(self, name=cookie_name, value=None, expires_days=30, version=None,
                          session_model: AbstractSession = session_model, user_model: AbstractUser = user_model,
                          **kwargs):
        self.set_cookie(name, self.create_signed_value(name, value,
                                                       version=version),
                        expires_days=expires_days, **kwargs)

    def get_secure_cookie(self, name=cookie_name, value=None, max_age_days=31,
                          min_version=None):
        self.require_setting("cookie_secret", "secure cookies")
        if value is None:
            value = self.get_cookie(name)
        return decode_signed_value(self.application.settings["cookie_secret"],
                                   name, value, max_age_days=max_age_days,
                                   min_version=min_version)

    def get_cookie(self, name, default=None):
        return super().get_cookie(name, default)

    def get_current_user(self, cookie_name=cookie_name, session_model: AbstractSession = session_model,
                         user_model: AbstractUser = user_model):
        if not issubclass(session_model, AbstractSession):
            raise ValueError('session model must a subclass with AbstractSession')
        if not issubclass(user_model, AbstractUser):
            raise ValueError('user model must a subclass with AbstractUser')
        session_key = self.get_secure_cookie(cookie_name)
        db_session = self.db_conn()
        session = db_session.query(session_model).filter(
            session_model.session_key == session_key, session_model.expire_date > datetime.datetime.now()).last()
        if session is not None:
            session_data = session.session_data
            json_data = base64.b64decode(session_data)
            json_data = json_data.replace(b"\'", b'"')
            session_data_dict = dict(json.loads(json_data))
            for value in session_data_dict.values():
                value = dict(value)
                user = db_session.query(user_model).filter(
                    user_model.userid == value.get('userid')).first()
                if user is not None:
                    return user
                else:
                    return ERROR_CODE_USER_NOT_FOUND
        return ERROR_CODE_TOKEN_ERROR

    def set_current_user(self, user: AbstractUser):
        if not isinstance(user, AbstractUser):
            raise ValueError('user must be a subclass with AbstractUser')
        self.current_user(user)


class APIHandler(BaseHandler, JSendMixin):
    """RequestHandler for API calls

    - Sets header as ``application/json``
    - Provides custom write_error that writes error back as JSON \
    rather than as the standard HTML template
    """
    cookie_name = 'apihelper_session'
    session_model = Session
    user_model = User

    def initialize(self):
        """
        - Set Content-type for JSON
        """
        self.set_header("Content-Type", "application/json")

    def write_error(self, status_code, **kwargs):
        """Override of RequestHandler.write_error

        Calls ``error()`` or ``fail()`` from JSendMixin depending on which
        exception was raised with provided reason and status code.

        :type  status_code: int
        :param status_code: HTTP status code
        """

        def get_exc_message(exception):
            return exception.log_message if \
                hasattr(exception, "log_message") else str(exception)

        self.clear()
        self.set_status(status_code)

        # Any APIError exceptions raised will result in a JSend fail written
        # back with the log_message as data. Hence, log_message should NEVER
        # expose internals. Since log_message is proprietary to HTTPError
        # class exceptions, all exceptions without it will return their
        # __str__ representation.
        # All other exceptions result in a JSend error being written back,
        # with log_message only written if debug mode is enabled
        exception = kwargs["exc_info"][1]
        if any(isinstance(exception, c) for c in [APIError, ValidationError]):
            # ValidationError is always due to a malformed request
            if isinstance(exception, ValidationError):
                self.set_status(400)
            self.fail(get_exc_message(exception))
        else:
            self.error(
                message=self._reason,
                data=get_exc_message(exception) if self.settings.get("debug")
                else None,
                code=status_code
            )


# 以下部分参考 https://blog.csdn.net/midion9/article/details/51332973
class LoginHandler(APIHandler):
    cookie_name = 'apihelper_session'
    session_model = Session
    user_model = User

    def get(self, cookie_name=cookie_name, *args, **kwargs):
        self.post(cookie_name, **kwargs)

    def post(self, cookie_name=cookie_name,
             session_model: AbstractSession = session_model,
             user_model: AbstractUser = user_model,
             *args, **kwargs):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        expires_days = self.settings.get('expires_days', 31)
        if not issubclass(session_model, AbstractSession):
            raise ValueError('session model must be subclass with AbstractSession')
        if not issubclass(user_model, AbstractUser):
            raise ValueError('user model must be subclass with AbstractUser')

        user = self.authenticate(username=username, password=password, *args, **kwargs)
        if user is not None:
            # 登录成功
            if not isinstance(user, AbstractUser):
                raise ValueError('authenticate must return an object subclass with AbstractUser')
            try:
                session_key = random_string(32)
                self.set_secure_cookie(cookie_name, session_key, expires_days=expires_days)
                db_session = self.db_conn()
                session_data = generate_session_data(user)
                obj = session_model(session_key=session_key, session_data=session_data,
                                    expire_date=datetime.timedelta(days=expires_days) + datetime.datetime.now())
                db_session.add(obj)
                db_session.commit()
                user_model.login_success(user, self)  # user log记录日志
                self.success(data="login successfully")
            except:
                self.error(data='login error', code=ERROR_CODE_DATABASE_ERROR)
        else:
            self.error(data="login error", code=ERROR_CODE_PARTNER_ERROR)

    @abstractmethod
    def authenticate(self, username, password, *args, **kwargs):
        pass


class WelcomeHandler(APIHandler):
    @authenticated
    def get(self, *args, **kwargs):
        user = self.current_user
        self.success('Welcome, {}'.format(user.username))


class LogoutHandler(APIHandler):
    cookie_name = 'apihelper_session'

    def get(self, cookie_name=cookie_name, *args, **kwargs):
        # cookie_name = self.get_argument('cookiename', 'apihelper_username')
        self.clear_cookie(cookie_name)
        self.success('logout successfully')


class SnowlandLoginHandler(LoginHandler):
    cookie_name = 'snolandapihelper_session'
    session_model = Session
    user_model = User

    def post(self, cookie_name=cookie_name,
             session_model: AbstractSession = session_model,
             user_model: AbstractUser = user_model, *args, **kwargs):
        super().post(cookie_name=cookie_name,
                     session_model=session_model,
                     user_model=user_model, **kwargs)

    @abstractmethod
    def authenticate(self, username, password, **kwargs):
        raise NotImplementedError
