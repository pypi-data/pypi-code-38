# -*- coding: utf-8 -*-

from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy_django import SQLAlchemy

db = SQLAlchemy(bind_key='auth')


class AuthSession(db.Model):
    __tablename__ = 'auth_session'

    session_key = Column(String(40), primary_key=True)
    session_data = Column(Text, nullable=False)
    expire_date = Column(DateTime, nullable=False)


class AuthUser(db.Model):
    __tablename__ = 'auth_user'

    id = Column(String, primary_key=True)
    login_name = Column(String(30), nullable=False)
    login_password = Column(String(256), nullable=False)
    first_name = Column(String(10), nullable=False)
    last_name = Column(String(20), nullable=False)
    user_name = Column(String(30), nullable=False)
    sex = Column(SmallInteger)
    phone_number = Column(String(11))
    email = Column(String(50))
    is_active = Column(SmallInteger, nullable=False)
    is_superuser = Column(SmallInteger, nullable=False)
    is_dba = Column(SmallInteger, nullable=False)
    is_read = Column(SmallInteger, nullable=False)
    is_leader = Column(SmallInteger, nullable=False)
    roles = Column(Text, nullable=False)
    create_date = Column(DateTime, nullable=False)
    last_login_date = Column(DateTime)
    last_login_ip = Column(String(32))
    wechat_json = Column(Text)
    extend_json = Column(Text)
    remark = Column(String(200))


class AuthGroup(db.Model):
    __tablename__ = 'auth_group'

    id = Column(String, primary_key=True)
    name = Column(String(50), nullable=False)
    type = Column(String(2), nullable=False)
    remark = Column(String(200))


class AuthGroupPermissions(db.Model):
    __tablename__ = 'auth_group_permissions'

    id = Column(String, primary_key=True)
    group_id = Column(ForeignKey(u'auth_group.id'))
    permission_id = Column(ForeignKey(u'auth_permission.id'))

    group = relationship(u'AuthGroup')
    permission = relationship(u'AuthPermission')


class AuthPermission(db.Model):
    __tablename__ = 'auth_permission'

    id = Column(String, primary_key=True)
    menu_name = Column(String(100), nullable=False)
    menu_url = Column(String(200))
    menu_url_alias = Column(String(200))
    menu_url_debug = Column(String(200))
    menu_target = Column(String(20))
    fast_url = Column(String(200))
    big_icon = Column(String(200))
    small_icon = Column(String(200))
    is_important = Column(SmallInteger, nullable=False)
    is_open = Column(SmallInteger, nullable=False)
    is_enable = Column(SmallInteger, nullable=False)
    is_cache = Column(SmallInteger)
    is_cross = Column(SmallInteger)
    is_debug = Column(SmallInteger)
    badge = Column(String(50))
    order_number = Column(Integer)
    status = Column(Integer)
    remark = Column(String(200))


class AuthPermissionRelation(db.Model):
    __tablename__ = 'auth_permission_relation'

    id = Column(String, primary_key=True)
    permission_id = Column(ForeignKey(u'auth_permission.id'))
    chailds = Column(ForeignKey(u'auth_permission.id'))
    depth = Column(SmallInteger, nullable=False)

    auth_permission = relationship(
        u'AuthPermission', primaryjoin='AuthPermissionRelation.chailds == AuthPermission.id')
    permission = relationship(
        u'AuthPermission', primaryjoin='AuthPermissionRelation.permission_id == AuthPermission.id')


class AuthUserLog(db.Model):
    __tablename__ = 'auth_user_log'

    id = Column(String, primary_key=True)
    user_id = Column(String(36), nullable=False)
    action_flag = Column(SmallInteger, nullable=False)
    action_time = Column(DateTime, nullable=False)
    ip = Column(String(32), nullable=False)
    action_class = Column(Text, nullable=False)
    action_object = Column(Text, nullable=False)
    action_handler = Column(String(200), nullable=False)
    status = Column(SmallInteger, nullable=False)
    status_note = Column(Text)


class MicroappApp(db.Model):
    __tablename__ = 'microapp_app'

    id = Column(String, primary_key=True)
    app_code = Column(String(10), nullable=False, unique=True)
    app_name = Column(String(20), nullable=False)
    app_secret = Column(String(36), nullable=False)
    app_summary = Column(Text)
    sso_url = Column(String(200), nullable=False)
    status = Column(SmallInteger, nullable=False)


class MicroappToken(db.Model):
    __tablename__ = 'microapp_token'

    id = Column(String, primary_key=True)
    app_id = Column(ForeignKey(u'microapp_app.id',
                               ondelete=u'RESTRICT', onupdate=u'RESTRICT'))
    app_secret = Column(String(36), nullable=False)
    token_code = Column(Text, nullable=False)
    grant_type = Column(String(20), nullable=False)
    session_id = Column(String(40), nullable=False)
    expire_date = Column(DateTime, nullable=False)

    app = relationship(u'MicroappApp')


class SysBlacklist(db.Model):
    __tablename__ = 'sys_blacklist'

    id = Column(String, primary_key=True)
    ip = Column(String(50), nullable=False)
    begin_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    remark = Column(String(200))


class SysBook(db.Model):
    __tablename__ = 'sys_book'

    id = Column(String, primary_key=True)
    class_code = Column(String(20), nullable=False)
    code = Column(String(50), nullable=False)
    text = Column(String(50), nullable=False)
    order_number = Column(SmallInteger, nullable=False)
    is_enable = Column(SmallInteger, nullable=False)
    remark = Column(String(200))


class SysConfig(db.Model):
    __tablename__ = 'sys_config'

    config_key = Column(String(20), primary_key=True)
    config_value = Column(Text, nullable=False)
    config_name = Column(String(200), nullable=False)


class SysCover(db.Model):
    __tablename__ = 'sys_cover'

    id = Column(String, primary_key=True)
    cover_title = Column(String(20), nullable=False)
    cover_summary = Column(Text, nullable=False)
    cover_image = Column(String(200), nullable=False)
    cover_thumbnail = Column(String(200))
    upload_date = Column(DateTime, nullable=False)
    upload_user = Column(String(20), nullable=False)
    order_number = Column(SmallInteger, nullable=False)
    remark = Column(String(200))


class SysGuest(db.Model):
    __tablename__ = 'sys_guest'

    id = Column(String, primary_key=True)
    ip = Column(String(50), nullable=False)
    request_date = Column(DateTime, nullable=False)
    location = Column(String(200))
    remark = Column(String(200))


class SysUpdateLog(db.Model):
    __tablename__ = 'sys_update_log'

    version_number = Column(String(50), primary_key=True)
    public_date = Column(DateTime, nullable=False)
    update_content = Column(Text, nullable=False)
    remark = Column(String(200))
