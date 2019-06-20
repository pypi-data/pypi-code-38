# -*- coding: utf-8 -*-
"""
This is the default implementation of the database backend of nao. It has a dependency
of sqlalchemy, but nothing sqlalchemy specific is exposed (?)

Maybe a basic sqlite implementation could also be supported here

"""

from __future__ import division, print_function, unicode_literals


from sqlalchemy.engine import create_engine
from sqlalchemy.types import Integer
from sqlalchemy.schema import Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr

#TODO: some logging facility is needed

# CONFIGURATION
# defaults
conf = {
    'host': '127.0.0.1',
    'port': 3306,
    'name': 'root',
    'pass': None,
    'db':   'test',
    }

# load YAML and update
conf.update(matrica.config['db'])
    # for k, v in params.iteritems(): params[k] = conf[k] if k in conf else v
cs = 'mysql://{name}:{pass}@{host}:{port}/{db}?charset=utf8'.format(**conf)
# log.error(cs)
engine = create_engine(cs)
# engine = create_engine('sqlite:///erih.db')
    # , echo=True
    # sqlite:///erih.db
    # server_local = r'\\VBMARI\Backup' # the runner needs to have access for that remote folder

Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
session = sess = s = Session()

# security measure to make session read-only
# session.flush = None

class DiffException(Exception): pass

class DatabaseGraph(object):
    """Creates a readable structure based on the definition

    joins realted classes etc
    """
    pass

class ModelBase(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__

    def xml(self, columns=None, subs=None):
        cols = [c.name for c in self.__table__.c] if columns is None else columns
        base = '<{0}{1} />' if subs is None else '<{0}{1}>'
        rows = []

        rows.append(base.format(
            self.__class__.__name__,
            ' ' + ' '.join('{0}="{1}"'.format(c, getattr(self, c, None)) for c in cols),

        ))

        if subs is not None:
            rows.extend(['  '+s for s in subs])
            rows.append('</{0}>'.format(self.__class__.__name__))

        return rows

    def verbose(self)        :
        return '\n'.join(self.xml())

    def __repr__(self):
        return '<{0} #{1}>'.format(self.__class__.__name__, getattr(self, 'id', ''))


Base = declarative_base(cls=ModelBase, bind=engine)











"""
IMPLEMENTATION DRAFT

this is an ORM specific implementation it should be covered with a standard interface
the multiprocess calculation and on demand query optimization should also be standardized
to be able to use a wide variety of storage not just relational databases

that is considered as an implementation detail but it will help later on
the primary data interface exposed is that of nao Entity structure itself

there might be a native implementation (without ORM), but that would be a lot of
maybe uneccesary work
"""

from sqlalchemy import declarative_base, engine, Column, LongInteger

class PrimaryEntityStore(Base):
    """
    this table holds the basic information on entities
    
    for quick access only an alive flag is available for historized access
    maybe a birth, death double date would be more suitable
    """
    id =        Column()
    name =      Column()
    aliases =   Column()
    

class PropertyMap(Base, LifeMixin)

    id
    base_entity
    prop_entity
    value =         # comprehensive not specific type (YAML maybe)
        # distinct query on values with daterange will be needed for the entity
        # to know what are the possible values
    
    
   
"""
we need to make a collection entity that collects other entities with a weighting

class ListEntity(Entity, list): pass
class DictEntity(Entity, dict): pass
class WeightedCollection(DictEntity): pass

also introduce probability attributes for all the numeric values with
single probabilities as well as distribution-based probabilities

summing probability over time, etc.

This might also be outside the scope of nao (maybe not possible)

"""


