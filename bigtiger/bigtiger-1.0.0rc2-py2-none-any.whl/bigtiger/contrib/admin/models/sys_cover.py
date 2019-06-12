# -*- coding: utf-8 -*-

"""
Sys_Cover
~~~~~~~~~~~~~

系统封面
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.forms.models import SQLAichemyModel

from bigtiger.contrib.admin.db_admin import db, SysCover


class SysCoverModel(SQLAichemyModel):
    """系统封面 Model"""

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(SysCover, sort), order)()
        return None

    def get_one(self, _id):
        row = self.session.query(SysCover).filter(
            SysCover.id == _id).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(SysCover)
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
        row = SysCover(**entity)
        self.session.add(row)
        self.session.commit()

    def modify(self, _id, new_entity):
        self.session.query(SysCover).filter(
            SysCover.id == _id).update(new_entity)
        self.session.commit()

    def delete(self, _id):
        self.session.query(SysCover).filter(SysCover.id == _id).delete()
        self.session.commit()

    def get_detail(self, _id):
        return self.get_one(_id)

    def get_page_query(self, cover_title, limit, offset, sort=None, order=None):
        query = self.session.query(SysCover).filter(
            SysCover.cover_title.contains(cover_title))

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
        query = self.session.query(SysCover).filter(SysCover.query)

        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows
        """

    def tran_import(self, lst):
        for item in lst:
            entity = SysCover(**item)
            self.session.add(entity)
        self.session.commit()

    def tran_add(self, entity):
        raise NotImplementedError

    def tran_modify(self, _id, new_entity):
        raise NotImplementedError

    def tran_delete(self, pks):

        self.session.query(SysCover).filter(
            SysCover.id.in_(pks)).delete(synchronize_session=False)

        self.session.commit()
