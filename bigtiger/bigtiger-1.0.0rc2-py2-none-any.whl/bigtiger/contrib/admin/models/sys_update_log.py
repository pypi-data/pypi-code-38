# -*- coding: utf-8 -*-

"""
Sys_Update_Log
~~~~~~~~~~~~~

系统更新日志
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.forms.models import SQLAichemyModel

from bigtiger.contrib.admin.db_admin import db, SysUpdateLog


class SysUpdateLogModel(SQLAichemyModel):
    """系统更新日志 Model"""

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(SysUpdateLog, sort), order)()
        return None

    def get_one(self, version_number):
        row = self.session.query(SysUpdateLog).filter(
            SysUpdateLog.version_number == version_number).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(SysUpdateLog)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def get_refer(self, version_number):

        query = sa.union_all()
        t = orm.aliased(query)
        rows = self.session.query(t).all_dict()
        return rows

    def add(self, entity):
        row = SysUpdateLog(**entity)
        self.session.add(row)
        self.session.commit()

    def modify(self, version_number, new_entity):
        self.session.query(SysUpdateLog).filter(
            SysUpdateLog.version_number == version_number).update(new_entity)
        self.session.commit()

    def delete(self, version_number):
        self.session.query(SysUpdateLog).filter(
            SysUpdateLog.version_number == version_number).delete()
        self.session.commit()

    def get_detail(self, version_number):
        return self.get_one(version_number)

    def get_page_query(self, limit, offset, sort=None, order=None):
        query = self.session.query(SysUpdateLog)

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

        """
        query = self.session.query(SysUpdateLog).filter(SysUpdateLog.query)

        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows
        """

    def tran_import(self, lst):
        for item in lst:
            entity = SysUpdateLog(**item)
            self.session.add(entity)
        self.session.commit()

    def tran_add(self, entity):
        raise NotImplementedError

    def tran_modify(self, version_number, new_entity):
        raise NotImplementedError

    def tran_delete(self, pks):

        self.session.query(SysUpdateLog).filter(
            SysUpdateLog.version_number.in_(pks)).delete(synchronize_session=False)

        self.session.commit()
