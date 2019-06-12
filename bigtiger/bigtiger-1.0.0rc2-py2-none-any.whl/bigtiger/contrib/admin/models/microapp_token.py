# -*- coding: utf-8 -*-

"""
微应用|会话票据
Created on 2017-07-19
@author: linkeddt.com
"""

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.forms.models import SQLAichemyModel

from bigtiger.contrib.admin.db_admin import db, MicroappToken, MicroappApp


class MicroappTokenModel(SQLAichemyModel):
    """微应用|会话票据 Model"""

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(MicroappToken, sort), order)()
        return None

    def get_one(self, _id):
        row = self.session.query(MicroappToken).filter(
            MicroappToken.id == _id).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(MicroappToken)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def get_list_app_id(self, app_id, sort=None, order=None):
        query = self.session.query(MicroappToken).filter(
            MicroappToken.app_id == app_id)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def add(self, entity):
        row = MicroappToken(**entity)
        self.session.add(row)
        self.session.commit()

    def modify(self, _id, new_entity):
        self.session.query(MicroappToken).filter(
            MicroappToken.id == _id).update(new_entity)
        self.session.commit()

    def delete(self, _id):
        self.session.query(MicroappToken).filter(
            MicroappToken.id == _id).delete()
        self.session.commit()

    def delete_app_id(self, app_id):
        self.session.query(MicroappToken).filter(
            MicroappToken.app_id == app_id).delete()
        self.session.commit()

    def get_detail(self, _id):
        return self.get_one(_id)

    def get_page_query(self, app_name, limit, offset, sort=None, order=None):
        query = self.session.query(MicroappToken, MicroappApp.app_name.label('app_name'), MicroappApp.app_code.label('app_code')).outerjoin(
            MicroappApp, MicroappApp.id == MicroappToken.app_id).filter(MicroappApp.app_name.contains(app_name))

        rows = None
        count = query.count()
        if count > 0:
            _sorted = self._get_sorted(sort, order)
            if _sorted is not None:
                query = query.order_by(_sorted)
            rows = query.limit(limit).offset(offset)
            rows = [dict(item.MicroappToken.to_dict(),
                         app_name=item.app_name, app_code=item.app_code) for item in rows]
        return rows, count

    def get_list_token_code(self, app_id, token_code):
        """根据token code 获取数据"""
        query = self.session.query(MicroappToken).filter(
            MicroappToken.token_code == token_code).filter(MicroappToken.app_id == app_id)
        rows = query.all_dict()
        return rows

    def tran_import(self, lst):
        for item in lst:
            entity = MicroappToken(**item)
            self.session.add(entity)
        self.session.commit()

    def tran_add(self, entity):
        raise NotImplementedError

    def tran_modify(self, _id, new_entity):
        raise NotImplementedError

    def tran_delete(self, pks):
        self.session.query(MicroappToken).filter(
            MicroappToken.id.in_(pks)).delete(synchronize_session=False)
        self.session.commit()
