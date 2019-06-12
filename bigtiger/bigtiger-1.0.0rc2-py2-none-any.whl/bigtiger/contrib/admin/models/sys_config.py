# -*- coding: utf-8 -*-

"""
系统配置
Created on 2017-07-19
@author: linkeddt.com
"""

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.forms.models import SQLAichemyModel

from bigtiger.contrib.admin.db_admin import db, SysConfig


class SysConfigModel(SQLAichemyModel):
    """系统配置 Model"""

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(SysConfig, sort), order)()
        return None

    def get_one(self, config_key):
        row = self.session.query(SysConfig).filter(
            SysConfig.config_key == config_key).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(SysConfig)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def get_refer(self, config_key):
        query = sa.union_all()
        t = orm.aliased(query)
        rows = self.session.query(t).all_dict()
        return rows

    def add(self, entity):
        row = SysConfig(**entity)
        self.session.add(row)
        self.session.commit()

    def modify(self, config_key, new_entity):
        self.session.query(SysConfig).filter(
            SysConfig.config_key == config_key).update(new_entity)
        self.session.commit()

    def delete(self, config_key):
        self.session.query(SysConfig).filter(
            SysConfig.config_key == config_key).delete()
        self.session.commit()

    def get_detail(self, config_key):
        return self.get_one(config_key)

    def get_page_query(self, config_key, config_name, limit, offset, sort=None, order=None):
        query = self.session.query(SysConfig).filter(
            SysConfig.config_key.contains(config_key)).filter(SysConfig.config_name.contains(config_name))

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
        query = self.session.query(SysConfig).filter(SysConfig.query)

        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows
        """

    def tran_import(self, lst):
        for item in lst:
            entity = SysConfig(**item)
            self.session.add(entity)
        self.session.commit()

    def tran_add(self, entity):
        raise NotImplementedError

    def tran_modify(self, config_key, new_entity):
        raise NotImplementedError

    def tran_delete(self, pks):
        self.session.query(SysConfig).filter(
            SysConfig.config_key.in_(pks)).delete(synchronize_session=False)
        self.session.commit()
