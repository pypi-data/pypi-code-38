# -*- coding: utf-8 -*-

"""
用户管理|用户日志
Created on 2017-07-19
@author: linkeddt.com
"""

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.forms.models import SQLAichemyModel

from bigtiger.contrib.admin.db_admin import db, AuthUserLog


class AuthUserLogModel(SQLAichemyModel):
    """用户管理|用户日志 Model"""

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(AuthUserLog, sort), order)()
        return None

    def get_one(self, _id):
        row = self.session.query(AuthUserLog).filter(
            AuthUserLog.id == _id).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(AuthUserLog)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def get_detail(self, _id):
        return self.get_one(_id)

    def get_page_query(self, action_flag, status, begin_date, end_date, action_class, limit, offset, sort=None, order=None):
        query = self.session.query(AuthUserLog).filter(
            sa.between(AuthUserLog.action_time, begin_date, end_date)).filter(AuthUserLog.action_class.contains(action_class))

        if action_flag != -1:
            query = query.filter(AuthUserLog.action_flag == action_flag)

        if status != 0:
            query = query.filter(AuthUserLog.status == status)

        rows = None
        count = query.count()
        if count > 0:
            _sorted = self._get_sorted(sort, order)
            if _sorted is not None:
                query = query.order_by(_sorted)
            rows = query.limit(limit).offset(offset).all_dict()
        return rows, count

    def add(self, entity):
        row = AuthUserLog(**entity)
        self.session.add(row)
        self.session.commit()
