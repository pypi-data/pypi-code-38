from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, raiseload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from .log import *

__engine_map = {}


def get_sqlalchemy_connection_address(label, database):
    host = config(label, 'host')
    port = config(label, 'port')
    user = config(label, 'user')
    password = config(label, 'password', '')
    if password == '':
        password = config(label, 'pass', '')
    return "mysql+pymysql://%s:%s@%s:%s/%s" % (user, password, host, port, database)


def get_sqlalchemy_engine(label, database=None):
    global __engine_map
    if not database:
        database = config(label, 'database')
    label1 = label + database
    if label1 in __engine_map:
        return __engine_map[label1]
    log_level = config('settings', 'log_level', 'info')
    pool_size = config('settings', 'pool_size', '30')
    engine = create_engine(get_sqlalchemy_connection_address(label, database), pool_size=int(pool_size),
                           pool_recycle=1800, echo=(log_level == 'debug'))
    __engine_map[label1] = engine
    return engine


def remove_sqlalchemy_engine(label, database=None):
    global __engine_map
    if not database:
        database = config(label, 'database')
    label1 = label + database
    if label1 in __engine_map:
        del __engine_map[label1]


def get_sqlalchemy_session(label, database):
    engine = get_sqlalchemy_engine(label, database)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # session_factory = sessionmaker(bind=engine)
    # session = scoped_session(session_factory)
    return session


def execute_sqlalchemy_sql(session, *multiparams, **params):
    return session.execute(*multiparams, **params)


def fetch_sqlalchemy_sql(session, *multiparams, **params):
    return session.execute(*multiparams, **params).fetchall()


def close_sqlalchemy_session(session):
    try:
        session.close()
    except:
        pass


Base = declarative_base()


class BaseModel:
    __label__ = None
    __database__ = None

    @classmethod
    def get_session(cls):
        return get_sqlalchemy_session(cls.__label__, cls.__database__)

    @classmethod
    def close_session(cls, session):
        if session is None:
            return
        close_sqlalchemy_session(session)

    @classmethod
    def save(cls, o, session=None):
        session1 = session
        if not session1:
            session1 = cls.get_session()
        session1.add(o)
        session1.commit()
        session1.refresh(o)
        if not session:
            cls.close_session(session1)

    @classmethod
    def save_quietly(cls, o, session=None):
        try:
            cls.save(o, session)
        except IntegrityError as ex:
            log_info('save_quietly exist dup item')
        except Exception as ex1:
            log_exception(ex1)
            raise ex1

    @classmethod
    def bulk_save(cls, o, session=None):
        try:
            cls._bulk_save0(o, session)
        except IntegrityError as ex:
            log_info('bulk_save exist dup items')
            for item in o:
                cls.save_quietly(item, session)
        except Exception as ex1:
            log_exception(ex1)
            raise ex1

    @classmethod
    def _bulk_save0(cls, o, session=None):
        session1 = session
        if not session1:
            session1 = cls.get_session()
        session1.bulk_save_objects(o)
        session1.commit()
        if not session:
            cls.close_session(session1)

    @classmethod
    def execute_sql(cls, session, *multiparams, **params):
        session1 = session
        if not session:
            session1 = cls.get_session()
        result = execute_sqlalchemy_sql(session1, *multiparams, **params)
        if not session:
            cls.close_session(session1)
        return result

    @classmethod
    def update_sql(cls, *multiparams, **params):
        session = cls.get_session()
        execute_sqlalchemy_sql(session, *multiparams, **params)
        session.commit()
        cls.close_session(session)

    @classmethod
    def fetch_sql(cls, *multiparams, **params):
        session = cls.get_session()
        result = fetch_sqlalchemy_sql(session, *multiparams, **params)
        cls.close_session(session)
        return result

    @classmethod
    def get_by_field(cls, field, value, session=None):
        session1 = session
        if not session1:
            session1 = cls.get_session()
        item = session1.query(cls).filter(field == value).options(raiseload('*')).first()
        if not session:
            cls.close_session(session1)
        return item

    @classmethod
    def get_by_id(cls, id, session=None):
        return cls.get_by_field(cls.id, id, session)

    @classmethod
    def get_by_fields(cls, field, values, session=None):
        try:
            session1 = session
            if not session1:
                session1 = cls.get_session()
            item = session1.query(cls).filter(field.in_(values)).options(raiseload('*')).all()
            if not session:
                cls.close_session(session1)
            return item
        except Exception as ex:
            log_exception(ex)
            return None

    @classmethod
    def get_all(cls, session=None):
        try:
            session1 = session
            if not session1:
                session1 = cls.get_session()
            item = session1.query(cls).options(raiseload('*')).all()
            if not session:
                cls.close_session(session1)
            return item
        except Exception as ex:
            log_exception(ex)
            return None

    @classmethod
    def get_by_ids(cls, ids, session=None):
        return cls.get_by_fields(cls.id, ids, session)

    def delete(self, session=None):
        try:
            session1 = session
            if not session1:
                session1 = self.get_session()
            session1.delete(self)
            session1.commit()
            if not session:
                self.close_session(session1)
        except Exception as ex:
            log_exception(ex)
            raise ex

    @classmethod
    def delete_by_id(cls, id):
        sql = "delete from {0} where id = :id".format(cls.__tablename__)
        cls.update_sql(sql, {'id': id})
        log_info("delete_by_id for {0} id={1}".format(cls.__tablename__, id))

    @classmethod
    def delete_all(cls, session=None):
        try:
            session1 = session
            if not session1:
                session1 = cls.get_session()
            num = session1.query(cls).delete()
            log_info("delete_all size=" + str(num))
            session1.commit()
            if not session:
                cls.close_session(session1)
        except Exception as ex:
            log_exception(ex)
            raise ex
