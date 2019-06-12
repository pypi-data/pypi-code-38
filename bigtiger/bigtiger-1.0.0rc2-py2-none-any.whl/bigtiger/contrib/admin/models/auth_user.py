# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.contrib.admin.db_admin import db, AuthUser


class AuthUserModel(object):
    """用户管理|用户信息 Model
    """

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(AuthUser, sort), order)()
        return None

    def get_one(self, _id):
        row = self.session.query(AuthUser).filter(
            AuthUser.id == _id).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(AuthUser)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def add(self, entity):
        row = AuthUser(**entity)
        self.session.add(row)
        self.session.commit()

    def modify(self, _id, new_entity):
        self.session.query(AuthUser).filter(
            AuthUser.id == _id).update(new_entity)
        self.session.commit()

    def delete(self, _id):
        refs = self.get_refer(_id)
        if refs:
            raise DBRefError(refs.pop())

        self.session.query(AuthUser).filter(AuthUser.id == _id).delete()
        self.session.commit()

    def get_detail(self, _id):
        query = self.session.query(AuthUser).\
            filter(AuthUser.id == _id)
        row = query.first_dict()
        return row

    def modify_pwd(self, _id, new_pwd):
        self.session.query(AuthUser).filter(
            AuthUser.id == _id).update({'login_password': new_pwd})
        self.session.commit()

    def get_one_login_name(self, login_name):
        row = self.session.query(AuthUser).filter(
            AuthUser.login_name == login_name).first_dict()
        return row

    def get_page_query(self, role_id, user_name, limit, offset, sort=None, order=None):
        """ 获取分页记录
        @param role_id: 所属角色id
        @param user_name: 用户姓名
        @return: 用户分页记录
        """
        query = self.session.query(AuthUser).\
            filter(AuthUser.user_name.contains(user_name)).\
            filter(AuthUser.is_superuser == 0)

        if role_id != '*':
            query = query.filter(AuthUser.roles.contains(role_id))

        rows = None
        count = query.count()
        if count > 0:
            _sorted = self._get_sorted(sort, order)
            if _sorted is not None:
                query = query.order_by(_sorted)
            rows = query.limit(limit).offset(offset).all_dict()
        return rows, count

    def get_list_query(self, query, sort=None, order=None):
        raise NotImplementedError

    def tran_import(self, lst):
        for item in lst:
            entity = AuthUser(**item)
            self.session.add(entity)
        self.session.commit()

    def tran_add(self, entity):
        raise NotImplementedError

    def tran_modify(self, _id, new_entity):
        raise NotImplementedError

    def tran_delete(self, pks):
        try:
            self.session.query(AuthUser).filter(
                AuthUser.id.in_(pks)).delete(synchronize_session=False)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise DBError(u'事务删除数据失败，请重试。')
