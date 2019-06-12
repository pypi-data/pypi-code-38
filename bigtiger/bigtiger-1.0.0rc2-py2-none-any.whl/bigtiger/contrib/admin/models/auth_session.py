# -*- coding: utf-8 -*-

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.contrib.admin.db_admin import AuthSession, db


class AuthSessionModel(object):

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(AuthSession, sort), order)()
        return None

    def get_one(self, session_key):
        row = self.session.query(AuthSession).filter(
            AuthSession.session_key == session_key).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(AuthSession)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def get_page_query(self, limit, offset, sort=None, order=None):
        query = self.session.query(AuthSession)

        rows = None
        count = query.count()
        if count > 0:
            _sorted = self._get_sorted(sort, order)
            if _sorted is not None:
                query = query.order_by(_sorted)
            rows = query.limit(limit).offset(offset)
            rows = [dict(session_key=row.session_key,
                         expire_date=row.expire_date, session_data='--):') for row in rows]
        return rows, count

    def add(self, entity):
        row = AuthSession(**entity)
        self.session.add(row)
        self.session.commit()

    def modify(self, session_key, new_entity):
        self.session.query(AuthSession).filter(
            AuthSession.session_key == session_key).update(new_entity)
        self.session.commit()

    def delete(self, session_key):
        self.session.query(AuthSession).filter(
            AuthSession.session_key == session_key).delete()
        self.session.commit()

    def exist_modify(self, entity):
        """
        如果数据存在则修改，不存在就新增.
        """
        session_key = entity['session_key']
        d = self.get_one(session_key)
        if d is None:
            self.add(entity)
        else:
            self.modify(session_key, entity)

    def tran_delete(self, pks):
        """
        删除多条会话数据.
        """
        self.session.query(AuthSession).filter(
            AuthSession.session_key.in_(pks)).delete(synchronize_session=False)
        self.session.commit()

    def tran_clear(self):
        """
        清空所有会话.
        """
        self.session.query(AuthSession).delete()
        self.session.commit()

    def tran_clear_expired(self):
        """
        清除过期的会话.
        """
        self.session.query(AuthSession).filter(
            AuthSession.expire_date.__lt__(datetime.now())).delete()
        self.session.commit()
