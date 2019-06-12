# -*- coding: utf-8 -*-

"""
用户管理|组信息
Created on 2017-07-19
@author: linkeddt.com
"""

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.forms.models import SQLAichemyModel

from bigtiger.contrib.admin.db_admin import db, AuthGroup, AuthGroupPermissions


class AuthGroupModel(SQLAichemyModel):
    """用户管理|组信息 Model
    """

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(AuthGroup, sort), order)()
        return None

    def get_one(self, _id):
        row = self.session.query(AuthGroup).filter(
            AuthGroup.id == _id).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(AuthGroup)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def get_refer(self, _id):

        q_authgrouppermissions = self.session.query(sa.literal('AuthGroupPermissions').label('ref_code'), sa.literal('用户管理|组权限信息').label('ref_desc'),
                                                    sa.func.count('*').label('ref_count')).select_from(AuthGroupPermissions).filter(AuthGroupPermissions.group_id == _id)

        query = sa.union_all(q_authusergroups, q_authgrouppermissions)
        t = orm.aliased(query)
        rows = self.session.query(t).all_dict()
        return rows

    def add(self, entity):
        row = AuthGroup(**entity)
        self.session.add(row)
        self.session.commit()

    def modify(self, _id, new_entity):
        self.session.query(AuthGroup).filter(
            AuthGroup.id == _id).update(new_entity)
        self.session.commit()

    def delete(self, _id):
        self.session.query(AuthGroup).filter(AuthGroup.id == _id).delete()
        self.session.commit()

    def get_detail(self, _id):
        return self.get_one(_id)

    def get_page_query(self, group_name, limit, offset, sort=None, order=None):
        query = self.session.query(AuthGroup).filter(
            AuthGroup.name.contains(group_name))

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
            entity = AuthGroup(**item)
            self.session.add(entity)
        self.session.commit()

    def tran_add(self, entity, group_permissions):
        row = AuthGroup(**entity)
        self.session.add(row)

        for p in group_permissions:
            row = AuthGroupPermissions(**p)
            self.session.add(row)
        self.session.commit()

    def tran_modify(self, _id, new_entity, group_permissions):
        self.session.query(AuthGroupPermissions).filter(
            AuthGroupPermissions.group_id == _id).delete(synchronize_session=False)

        self.session.query(AuthGroup).filter(
            AuthGroup.id == _id).update(new_entity)

        for p in group_permissions:
            row = AuthGroupPermissions(**p)
            self.session.add(row)
        self.session.commit()

    def tran_delete(self, pks):
        self.session.query(AuthGroupPermissions).filter(
            AuthGroupPermissions.group_id.in_(pks)).delete(synchronize_session=False)

        self.session.query(AuthGroup).filter(
            AuthGroup.id.in_(pks)).delete(synchronize_session=False)

        self.session.commit()
