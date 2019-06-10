#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
import uuid
from base64 import b64encode
from datetime import datetime
from decimal import Decimal

from pysmx.crypto import hashlib
from sqlalchemy import Column, Integer, String, DateTime  # 相应的列
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base  # db 基类
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.types import Text
from apihelper.util.hashers import BasePasswordHasher, SM3PasswordHasher
from apihelper.security.crypto import check_password, make_password


__Base = declarative_base()


class Base(__Base):
    __abstract__ = True

    def to_dict(self, filds=[]):
        items = {}
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            val = '' if val is None else val
            if isinstance(val, Decimal):
                val = str(val)
            if type(filds) == list and len(filds) > 0:
                if column.name in filds:
                    items[column.name] = val
            else:
                items[column.name] = val
        return items

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class AbstractRole(Base):
    """
    role model
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, nullable=False, default=None)
    rolename = Column(String(40), nullable=False)
    permission = Column(Text, default='')
    sort = Column(Integer, nullable=False, default=20)
    # 状态:( 0 禁用；1 启用, 默认1)
    status = Column(Integer, nullable=False, default=1)
    utc_created_at = Column(TIMESTAMP, default=datetime.now())

    @classmethod
    def option_html(cls, role_id=None):
        query = cls.session.query(Role)
        query = query.filter(Role.status == 1)
        rows = query.order_by(Role.sort.asc()).all()
        # SysLogger.debug(query.statement)
        option_str = ''
        for row in rows:
            selected = 'selected' if role_id == row.id else ''
            option_str += '<option value="%s" %s>%s</option>' % (row.id, selected, row.rolename)
        # SysLogger.debug('option_str: %s' % option_str)
        return option_str

    @classmethod
    def get_permission(cls, role_id):
        query = cls.session.query('permission')
        query = query.filter(Role.id == role_id)
        return query.scalar()


class Role(AbstractRole):
    """
    role model
    """
    __tablename__ = 'sys_admin_role'


class AbstractUser(Base):
    """
    user model
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, nullable=False, default=None)
    userid = Column(String(64), unique=True, default=str(uuid.uuid4()))
    role_id = Column(Integer, ForeignKey('sys_admin_role.id'))
    password = Column(String(128), nullable=False, default='')
    username = Column(String(40), nullable=False)
    mobile = Column(String(11), nullable=True)
    email = Column(String(80), nullable=True)
    permission = Column(Text, default='')
    login_count = Column(Integer, nullable=False, default=0)
    last_login_ip = Column(String(128), nullable=False, default='')
    # 用户状态:(0 锁定, 1正常, 默认1)
    status = Column(Integer, nullable=False, default=1)
    utc_last_login_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)
    utc_created_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    @property
    def role_permission(self):
        query = "select permission from sys_admin_role where id='%s'" % self.role_id
        permission = User.session.execute(query).scalar()
        try:
            return json.loads(permission)
        except BaseException as e:
            pass
            # raise e
        return []

    @classmethod
    def get_permission(cls):
        try:
            return json.loads(cls.permission)
        except Exception as e:
            pass
            # raise e
        return []

    @staticmethod
    def login_success(user, handler):
        # 设置登录用户cookie信息
        handler.set_current_user(user)

        user_id = user.id
        login_count = user.login_count if user.login_count else 0
        params = {
            'login_count': login_count + 1,
            'utc_last_login_at': datetime.now(),
            'last_login_ip': handler.request.remote_ip,
        }
        db_session = handler.db_conn()
        user_model = user.__class__
        db_session.query(user_model).filter(user_model.id == user_id).update(params)
        params = {
            'user_id': user.id,
            'client': 'web',
            'ip': handler.request.remote_ip,
        }
        log = UserLoginLog(**params)

        db_session.add(log)
        db_session.commit()
        return True

    def set_password(self, raw_password, salt=None, hasher='default'):
        self.password = make_password(raw_password, salt, hasher)

    def check_password(self, raw_password, setter=None, preferred='default'):
        return check_password(raw_password, setter, preferred)

    @classmethod
    def createuser(cls, username, password=None, salt=None, hasher='default', **kwargs):
        password = make_password(password, salt=salt, hasher=hasher)
        user = cls.__new__(username, password, **kwargs)
        return user

class User(AbstractUser):
    __tablename__ = 'sys_admin_user'
    role_id = Column(Integer, ForeignKey('sys_admin_role.id'))


class AbstractUserLoginLog(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, nullable=False, default=None)
    user_id = Column(Integer, ForeignKey('sys_admin_user.id'))
    ip = Column(String(40), nullable=False)
    client = Column(String(20), nullable=True)
    utc_created_at = Column(TIMESTAMP, default=datetime.now())


class UserLoginLog(AbstractUserLoginLog):
    """
    user model
    """
    __tablename__ = 'sys_admin_user_login_log'
    user_id = Column(Integer, ForeignKey('sys_admin_user.id'))


class AbstractAdminMenu(Base):
    """
    user group map model
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, nullable=False, default=None)
    user_id = Column(Integer, ForeignKey('sys_admin_user.id'), nullable=False, default='0')
    parent_id = Column(Integer, nullable=False, default=0)
    code = Column(String(64), nullable=True)
    title = Column(String(20), nullable=False)
    icon = Column(String(20), nullable=False)
    path = Column(String(200), nullable=False)
    param = Column(String(200), nullable=False)
    target = Column(String(20), nullable=False, default='_self')
    nav = Column(Integer, nullable=False)
    sort = Column(Integer, nullable=False, default=20)
    system = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    utc_created_at = Column(TIMESTAMP, default=datetime.now())

    @classmethod
    def info(cls, id=None, path=None):
        """获取当前访问节点信息

        [description]

        Keyword Arguments:
            id {str} -- [description] (default: {''})

        Returns:
            [type] -- [description]
        """
        query = cls.session.query(AdminMenu)
        if id:
            query = query.filter(AdminMenu.id == id)
        if path:
            path = path.split('?')[0]
            if path.endswith('/'):
                path = path[:-1]
            if path.endswith('.html'):
                path = path[:-5]

            query = query.filter(AdminMenu.path == path)

        row = query.first()
        row = row.to_dict() if row else None
        # SysLogger.debug(query.statement)
        return row

    @classmethod
    def brand_crumbs(cls, id):
        """获取当前节点的面包屑

        [description]

        Arguments:
            id {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        menu = []
        row = cls.info(id=id)
        if row['parent_id'] > 0:
            menu.append(row)
            child = cls.brand_crumbs(row['parent_id'])
            if len(child):
                menu.extend(child)
        return menu

    @classmethod
    def main_menu(cls, parent_id=0, status=1, level=0):
        """获取后台主菜单(一级 > 二级 > 三级)
            后台顶部和左侧使用

            Keyword Arguments:
                parent_id {str} -- 父ID (default: {'0'})
                level {number} -- 层级数 (default: {0})
            Returns:
                [type] -- [description]
        """
        trees = []
        if not len(trees):
            filds = ['id', 'code', 'parent_id', 'title', 'path', 'param', 'target', 'icon']
            query = cls.session.query(AdminMenu)
            if status is not None:
                query = query.filter(AdminMenu.status == status)
            query = query.filter(AdminMenu.nav == 1)
            rows = query.order_by(AdminMenu.sort.asc()).all()
            # print('query.statement: ', query.statement)
            for row in rows:
                row = row.as_dict(filds)
                if row.get('parent_id') != parent_id:
                    continue

                if level == 5:
                    return trees
                row['children'] = cls.main_menu(row.get('id'), status, level + 1)
                trees.append(row)
        return trees

    @staticmethod
    def children(parent_id=0, status=None, level=0, user_id=''):
        """获取指定节点下的所有子节点(不含快捷收藏的菜单)
        """
        trees = []
        if not len(trees):
            filds = ['id', 'code', 'parent_id', 'title', 'path', 'param', 'target', 'icon', 'sort', 'status']
            query = AdminMenu.session.query(AdminMenu)
            if user_id:
                query = query.filter(AdminMenu.user_id == user_id)
            query = query.filter(AdminMenu.parent_id == parent_id)
            if status in [1, 0]:
                query = query.filter(AdminMenu.status == status)
            rows = query.order_by(AdminMenu.sort.asc()).all()
            data = []
            for row in rows:
                if level == 5:
                    return trees
                row = row.to_dict(filds)

                row['children'] = AdminMenu.children(row.get('id'), status, level + 1)
                trees.append(row)
        return trees

    @staticmethod
    def menu_option(id=''):
        """菜单选项"""
        menus = AdminMenu.main_menu(status=None)
        if not len(menus) > 0:
            return ''
        option1 = '<option level="1" value="%s" %s>— %s</option>'
        option2 = '<option level="2" value="%s" %s>—— %s</option>'
        option3 = '<option level="3" value="%s" %s>——— %s</option>'
        html = ''
        for menu in menus:
            selected = 'selected' if id == menu.get('id', '') else ''
            title1 = menu.get('title', '')
            children1 = menu.get('children', [])
            html += option1 % (menu.get('id', ''), selected, title1)
            if not len(children1) > 0:
                continue
            for menu2 in children1:
                selected2 = 'selected' if id == menu2.get('id', '') else ''
                title2 = menu2.get('title', '')
                children2 = menu2.get('children', [])
                html += option2 % (menu2.get('id', ''), selected2, title2)
                if not len(children2) > 0:
                    continue
                for menu3 in children2:
                    selected3 = 'selected' if id == menu3.get('id', '') else ''
                    title3 = menu3.get('title', '')
                    html += option3 % (menu3.get('id', ''), selected3, title3)
        return html


class AdminMenu(AbstractAdminMenu):
    """
    user group map model
    """
    __tablename__ = 'sys_admin_menu'
    user_id = Column(Integer, ForeignKey('sys_admin_user.id'), nullable=False, default='0')


class AbstractSession(Base):
    __abstract__ = True
    session_key = Column(String(64), primary_key=True, nullable=False, unique=True)
    session_data = Column(Text)
    expire_date = Column(DateTime)


def generate_session_data(user: AbstractUser):
    if isinstance(user, AbstractUser):
        sm3 = hashlib.sm3()
        sm3.update(str(datetime.now()))
        key = sm3.hexdigest()
        return b64encode(bytes(str({key: {"userid": user.userid}}), encoding='utf-8'))
    return None


class Session(AbstractSession):
    __tablename__ = 'sys_session'


def get_sqlalchemy_url(driver, username, password, host='localhost', port=3306, dbname=None) -> str:
    return '%s://%s:%s@%s:%d/%s' % (driver, username, password, host, port, dbname)
