# -*- coding:utf-8 -*-


from .setting import *


class AppRouter(object):
    """
    A router to control all database operations on models for different
    databases. Original by Diego Búrigo Zacarão (http://diegobz.net/2011/02/10/django-database-router-using-settings/)
    Edited by Yangdw to fit Django 1.8.

    In case an app is not set in APP_DATABASE_MAPPING, the router
    will fallback to the `default` database.

    Settings example:

    APP_DATABASE_MAPPING = {'app1': 'db1', 'app2': 'db2'}
    """

    def db_for_read(self, model, **hints):
        """Point all read operations to the specific database."""
        return self.mapping.get(model._meta.app_label)

    def db_for_write(self, model, **hints):
        """Point all write operations to the specific database."""
        return self.mapping.get(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation between apps that use the same database."""
        db_obj1 = self.mapping.get(obj1._meta.app_label, 'default')
        db_obj2 = self.mapping.get(obj2._meta.app_label, 'default')
        if db_obj1 and db_obj2:
            if db_obj1 == db_obj2:
                return True
            else:
                return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Make sure that apps only appear in the related database."""
        prescribed_db = self.mapping.get(app_label)
        if prescribed_db is None:
            if db == 'default':
                return None
            else:
                return False
        return db == prescribed_db

    @property
    def mapping(self):
        return get_setting('APP_DATABASE_MAPPING', {})
