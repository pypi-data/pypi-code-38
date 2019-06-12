# -*- coding: utf-8 -*-

"""
系统数据字典
Created on 2017-07-19
@author: linkeddt.com
"""

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.forms.models import SQLAichemyModel

from bigtiger.contrib.admin.db_admin import db, SysBook


class SysBookModel(SQLAichemyModel):
    """系统数据字典 Model"""

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(SysBook, sort), order)()
        return None

    def get_one(self, _id):
        row = self.session.query(SysBook).filter(
            SysBook.id == _id).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(SysBook)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def add(self, entity):
        row = SysBook(**entity)
        self.session.add(row)
        self.session.commit()

    def modify(self, _id, new_entity):
        self.session.query(SysBook).filter(
            SysBook.id == _id).update(new_entity)
        self.session.commit()

    def delete(self, _id):
        self.session.query(SysBook).filter(SysBook.id == _id).delete()
        self.session.commit()

    def get_detail(self, _id):
        return self.get_one(_id)

    def get_page_query(self, class_code, code, text, remark, limit, offset, sort=None, order=None):
        query = self.session.query(SysBook).filter(
            SysBook.class_code.contains(class_code)).filter(
                SysBook.code.contains(code)).filter(
                    SysBook.text.contains(text)).filter(
                        SysBook.remark.contains(remark))

        rows = None
        count = query.count()
        if count > 0:
            _sorted = self._get_sorted(sort, order)
            if _sorted is not None:
                query = query.order_by(_sorted)
            rows = query.limit(limit).offset(offset).all_dict()
        return rows, count

    def get_list_class_code(self, class_code, sort=None, order=None):
        query = self.session.query(SysBook).filter(
            SysBook.class_code == class_code).filter(SysBook.is_enable == 1)

        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def tran_import(self, lst):
        for item in lst:
            entity = SysBook(**item)
            self.session.add(entity)
        self.session.commit()

    def tran_add(self, entity):
        raise NotImplementedError

    def tran_modify(self, _id, new_entity):
        raise NotImplementedError

    def tran_delete(self, pks):
        self.session.query(SysBook).filter(
            SysBook.id.in_(pks)).delete(synchronize_session=False)
        self.session.commit()
