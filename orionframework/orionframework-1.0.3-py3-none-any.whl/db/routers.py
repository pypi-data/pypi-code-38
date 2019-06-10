#
# Example:
#
# on routers.py
#
# from orionframework.db.routers import DatabaseRouter
#
# class YourRouter(DatabaseRouter):
#
#    db_name = "your_db_name"
#    models = [...]
#    modules = [...]
#
# on settings.py add
#
# DATABASE_ROUTERS = ['xxx.routers.YourRouter']
#

class DatabaseRouter(object):
    """
    A router to control database routing so specific models or modules are
    directed to a specific table

    @author: Ivanir Joao Kreuzberg
    """

    db_name = None
    models = []
    modules = []

    def match(self, model):

        if self.modules.__contains__(model._meta.app_label):
            return True

        if self.models.__contains__(model._meta.model_name):
            return True

        return False

    def db_for_read(self, model, **hints):

        if self.match(model):
            return self.db_name

        return None

    def db_for_write(self, model, **hints):

        if self.match(model):
            return self.db_name

        return None

    def allow_relation(self, obj1, obj2, **hints):

        if self.match(obj1) and self.match(obj2):
            return True

        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        if db == self.db_name:
            return False

        return None
