# Created by Q-ays.
# whosqays@gmail.com

# install sqlalchemy before use

# postgres tools

from sqlalchemy.exc import SQLAlchemyError, TimeoutError
import traceback
import json


def session_exception(session, is_raise=True):
    def wrapper(func):

        def catch(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except SQLAlchemyError as e:
                # print(e)
                print('~~~~~~~~~~~~~~~~session error~~~~~~~~~~~~~~~~~~')
                traceback.print_exc()
                if not isinstance(e, TimeoutError):
                    session.rollback()
                if is_raise:
                    raise e

        return catch

    return wrapper


def to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


def str2js(ls):
    """
    json字符转字典
    :param ls:
    :return:
    """
    if isinstance(ls, list):
        ls0 = list()

        try:
            for l in ls:
                ls0.append(json.loads(l))

            return ls0
        except:
            pass

    return ls


def detect_filed(o, *args):
    """
    特定字段字符转json
    :param o:
    :param args:
    :return:
    """
    for arg in args:
        n = o.get(arg)
        if n:
            o[arg] = str2js(n)

    return o


def o2d(obj):
    """
    把对象(支持单个对象、list、set)转换成字典
    针对postgres数据库
    :param obj: obj, list, set
    :return:
    """

    if isinstance(obj, dict) or (not obj):
        return obj

    is_list = isinstance(obj, list)
    is_set = isinstance(obj, set)

    if is_list or is_set:
        obj_arr = []

        for o in obj:
            if o:
                if isinstance(o, dict):
                    n = detect_filed(o, 'roles', 'org')
                else:
                    n = detect_filed(o.to_dict(), 'roles', 'org')

                obj_arr.append(n)
        return obj_arr
    else:
        return detect_filed(obj.to_dict(), 'roles', 'org')


def repo_ref(session0):
    """
    基于postgres 数据库增删改查的公共类
    :param session0:
    :return:
    """
    class RepoBase:
        def __init__(self, Model=None):
            self.session = session0
            self.Model = Model

        def add(self, **data):
            model0 = self.Model(**data)

            self.session.add(model0)
            self.session.commit()

            return model0

        def delete(self, did):
            repo = self.session.query(self.Model).get(did)

            self.session.delete(repo)
            self.session.commit()

            return repo

        def update(self, did, **data):
            model0 = self.get(did)

            columns = model0.__table__.columns

            for col in columns:
                name = col.name
                value = data.get(name, None)

                if value and not col.primary_key:
                    print(name)
                    setattr(model0, name, value)

            self.session.commit()

            return model0

        def get(self, did=None, **kwargs):
            if did:
                repos = self.session.query(self.Model).get(did)
            elif kwargs:
                repos = self.session.query(self.Model).filter_by(**kwargs).all()
            else:
                repos = self.session.query(self.Model).all()

            return repos

    return RepoBase
