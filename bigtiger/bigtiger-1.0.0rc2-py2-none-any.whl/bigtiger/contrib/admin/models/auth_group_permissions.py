# -*- coding: utf-8 -*-

"""
Auth_Group_Permissions
~~~~~~~~~~~~~

用户管理|组权限信息
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.forms.models import SQLAichemyModel

from bigtiger.contrib.admin.db_admin import db, AuthGroupPermissions


class AuthGroupPermissionsModel(SQLAichemyModel):
    """用户管理|组权限信息 Model"""

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(AuthGroupPermissions, sort), order)()
        return None

    def get_one(self, _id):
        row = self.session.query(AuthGroupPermissions).filter(
            AuthGroupPermissions.id == _id).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(AuthGroupPermissions)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def get_list_group_id(self, group_id, sort=None, order=None):
        query = self.session.query(AuthGroupPermissions).filter(
            AuthGroupPermissions.group_id == group_id)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def get_list_permission_id(self, permission_id, sort=None, order=None):
        query = self.session.query(AuthGroupPermissions).filter(
            AuthGroupPermissions.permission_id == permission_id)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def get_refer(self, _id):

        query = sa.union_all()
        t = orm.aliased(query)
        rows = self.session.query(t).all_dict()
        return rows

    def add(self, entity):
        row = AuthGroupPermissions(**entity)
        self.session.add(row)
        self.session.commit()

    def modify(self, _id, new_entity):
        self.session.query(AuthGroupPermissions).filter(
            AuthGroupPermissions.id == _id).update(new_entity)
        self.session.commit()

    def delete(self, _id):
        self.session.query(AuthGroupPermissions).filter(
            AuthGroupPermissions.id == _id).delete()
        self.session.commit()

    def delete_group_id(self, group_id):
        self.session.query(AuthGroupPermissions).filter(
            AuthGroupPermissions.group_id == group_id).delete()
        self.session.commit()

    def delete_permission_id(self, permission_id):
        self.session.query(AuthGroupPermissions).filter(
            AuthGroupPermissions.permission_id == permission_id).delete()
        self.session.commit()

    def get_detail(self, _id):
        return self.get_one(_id)

    def get_page_query(self, query, limit, offset, sort=None, order=None):
        raise NotImplementedError

        """
        query = self.session.query(AuthGroupPermissions).filter(AuthGroupPermissions.query)

        rows = None
        count = query.count()
        if count > 0:
            _sorted = self._get_sorted(sort, order)
            if _sorted is not None:
                query = query.order_by(_sorted)
            rows = query.limit(limit).offset(offset).all_dict()
        return rows, count
        """

    def get_list_query(self, query, sort=None, order=None):
        raise NotImplementedError

        """
        query = self.session.query(AuthGroupPermissions).filter(AuthGroupPermissions.query)

        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows
        """

    def tran_import(self, lst):
        for item in lst:
            entity = AuthGroupPermissions(**item)
            self.session.add(entity)
        self.session.commit()

    def tran_add(self, entity):
        raise NotImplementedError

    def tran_modify(self, _id, new_entity):
        raise NotImplementedError

    def tran_delete(self, pks):

        self.session.query(AuthGroupPermissions).filter(
            AuthGroupPermissions.id.in_(pks)).delete(synchronize_session=False)

        self.session.commit()
