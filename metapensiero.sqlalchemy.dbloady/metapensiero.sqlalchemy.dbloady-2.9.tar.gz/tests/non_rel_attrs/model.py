# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Non-relationship attributes test
# :Created:   lun 07 nov 2016 10:40:00 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

import sys

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()

class Person(Base):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(64))
    lastname = Column(String(64))


class CannedFilter(Base):
    __tablename__ = 'filters'

    id = Column(Integer, primary_key=True)
    description = Column(String(64))


class Condition(Base):
    __tablename__ = 'conditions'

    id = Column(Integer, primary_key=True)
    idfilter = Column(Integer,
                      ForeignKey('filters.id', ondelete='CASCADE'),
                      nullable=False)
    fieldname = Column(String(64))
    fieldvalue = Column(String(64))

    filter = relationship('CannedFilter')


url = 'sqlite:////tmp/testdbloady.sqlite'
e = create_engine(url)

if len(sys.argv) == 2:
    if sys.argv[1] == 'setup':
        Base.metadata.create_all(e)
    elif sys.argv[1] == 'test':
        smaker = sessionmaker(autoflush=False, autocommit=False, bind=e)
        session = smaker()

        condition = session.query(Condition).one()
        assert condition.filter.description == 'Only John Doe'
        assert condition.fieldname == 'persons.id'

        person = session.query(Person).get(condition.fieldvalue)
        assert person.lastname == 'Doe'
