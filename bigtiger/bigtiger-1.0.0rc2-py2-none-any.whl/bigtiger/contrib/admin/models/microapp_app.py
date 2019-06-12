# -*- coding: utf-8 -*-

"""
微应用|应用信息
Created on 2017-07-19
@author: linkeddt.com
"""

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.forms.models import SQLAichemyModel

from bigtiger.contrib.admin.db_admin import db, MicroappApp, MicroappToken


class MicroappAppModel(SQLAichemyModel):
    """微应用|应用信息 Model"""

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(MicroappApp, sort), order)()
        return None

    def get_one(self, _id):
        row = self.session.query(MicroappApp).filter(
            MicroappApp.id == _id).first_dict()
        return row

    def get_one_app_code(self, app_code):
        row = self.session.query(MicroappApp).filter(
            MicroappApp.app_code == app_code).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(MicroappApp)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def get_refer(self, _id):

        q_microapptoken = self.session.query(sa.literal('MicroappToken').label('ref_code'), sa.literal('微应用|会话票据').label('ref_desc'),
                                             sa.func.count('*').label('ref_count')).select_from(MicroappToken).filter(MicroappToken.app_id == _id)

        query = sa.union_all(q_microapptoken)
        t = orm.aliased(query)
        rows = self.session.query(t).all_dict()
        return rows

    def add(self, entity):
        row = MicroappApp(**entity)
        self.session.add(row)
        self.session.commit()

    def modify(self, _id, new_entity):
        self.session.query(MicroappApp).filter(
            MicroappApp.id == _id).update(new_entity)
        self.session.commit()

    def delete(self, _id):
        self.session.query(MicroappToken).filter(
            MicroappToken.app_id == _id).delete()
        self.session.query(MicroappApp).filter(MicroappApp.id == _id).delete()
        self.session.commit()

    def get_detail(self, _id):
        return self.get_one(_id)

    def get_page_query(self, app_name, limit, offset, sort=None, order=None):
        query = self.session.query(MicroappApp).filter(
            MicroappApp.app_name.contains(app_name))

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
            entity = MicroappApp(**item)
            self.session.add(entity)
        self.session.commit()

    def tran_add(self, entity):
        raise NotImplementedError

    def tran_modify(self, _id, new_entity):
        raise NotImplementedError

    def tran_delete(self, pks):
        self.session.query(MicroappApp).filter(
            MicroappApp.id.in_(pks)).delete(synchronize_session=False)
        self.session.commit()
