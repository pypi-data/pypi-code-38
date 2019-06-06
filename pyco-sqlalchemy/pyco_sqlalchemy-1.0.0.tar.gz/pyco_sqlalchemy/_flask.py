from datetime import datetime
from pprint import pformat
import logging

from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.attributes import InstrumentedAttribute
from flask_sqlalchemy import SQLAlchemy
import werkzeug.exceptions as errors
import flask

session_options = dict(
    bind=None,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
db = SQLAlchemy(session_options=session_options)

if flask.has_app_context():
    logger = flask.current_app.logger
else:
    logger = logging.getLogger("flask.app")


def force_remove_multiple(*models, silent=False):
    count = 0
    for m in models:
        if isinstance(m, db.Model):
            db.session.delete(m)
            count += 1
        else:
            msg = "DbModel Not Found:<{}:{}>".format(type(m), m)
            if silent:
                logger.error(msg)
            else:
                db.session.rollback()
                raise errors.NotFound(msg)
    if count > 0:
        db.session.commit()
        db.session.close()


class BaseModel():
    """ sample:
    >>> class TableName(db.Model, BaseModel):
        pass
    """

    @classmethod
    def columns(cls):
        tbl = getattr(cls, "__table__", None)
        if tbl is None:
            name = cls.__name__
            desc = 'Service Unavailable: DbModel<{}> '.format(name)
            msg = "API-ERROR:{}\nDbModel<{}> must be subclass of db.Model!".format(desc, name)
            logger.error(msg)
            raise errors.ServiceUnavailable(desc)
        else:
            return tbl.columns

    @classmethod
    def primary_keys(cls):
        tbl = cls.__table__
        pks = [m.name for m in tbl.primary_key.columns]
        return pks

    @classmethod
    def _immutable_keys(cls):
        # limit columns should not updated by cls.update(form)
        pks = cls.primary_keys()
        return pks

    @classmethod
    def strict_form(cls, data=None, **kwargs):
        if data is None:
            data = kwargs
        elif isinstance(data, dict):
            data.update(**kwargs)
        else:
            raise TypeError('data value must be dict or None')

        form = {}
        for k, v in data.items():
            col = getattr(cls, k, None)
            if isinstance(col, InstrumentedAttribute):
                if isinstance(v, str):
                    v = v.strip()
                form[k] = v
        return form

    @classmethod
    def initial(cls, data=None, **kwargs):
        form = cls.strict_form(data, **kwargs)
        m = cls(**form)
        return m

    @classmethod
    def insert(cls, data=None, **kwargs):
        m = cls.initial(data, **kwargs)
        m.save()
        return m

    @classmethod
    def count(cls, condition=None, **condition_kws):
        # https://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query.count
        cond = cls.strict_form(condition, **condition_kws)
        pk = cls.primary_keys()[0]
        qry = cls.query.filter_by(**cond).value(func.count(getattr(cls, pk)))
        return qry

    @classmethod
    def filter_by(cls, condition=None, **condition_kws):
        cond = cls.strict_form(condition, **condition_kws)
        ms = cls.query.filter_by(**cond).all()
        return ms

    @classmethod
    def get_or_none(cls, condition=None, **condition_kws):
        cond = cls.strict_form(condition, **condition_kws)
        return cls.query.filter_by(**cond).one_or_none()

    @classmethod
    def upsert_one(cls, condition: dict, **updated_kws):
        m = cls.get_or_none(condition)
        if isinstance(m, cls):
            m.update(updated_kws)
        else:
            m = cls.insert(condition, **updated_kws)
        return m

    @classmethod
    def getOr404(cls, **condition_kws):
        m = cls.get_or_none(condition_kws)
        if isinstance(m, cls):
            return m
        else:
            name = cls.__name__
            msg = "Data Not Found: {}: {}".format(name, pformat(condition_kws))
            raise errors.NotFound(msg)

    def to_dict(self, **kwargs):
        d = dict(
            _type=self.__class__.__name__
        )
        columns = self.columns()
        for col in columns:
            name = col.name
            value = getattr(self, name)
            d[name] = value
        d.update(kwargs)
        return d

    def update(self, form=None, __force=False, **kwargs):
        data = self.strict_form(form, **kwargs)
        keys = self._immutable_keys()
        for k, v in data.items():
            is_mutable = k not in keys
            if __force or is_mutable:
                setattr(self, k, v)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()
        db.session.close()

    def remove(self):
        db.session.delete(self)
        db.session.commit()
        db.session.close()


class CoModel(BaseModel):
    @declared_attr
    def created_time(self):
        return db.Column(db.DateTime, default=datetime.utcnow)

    @declared_attr
    def updated_time(self):
        return db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
