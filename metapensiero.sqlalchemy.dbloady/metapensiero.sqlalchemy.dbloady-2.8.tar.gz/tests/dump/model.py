# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Test model
# :Created:   ven 08 gen 2016 12:27:26 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import sys

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Person(Base):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(64))
    lastname = Column(String(64))


class Exam(Base):
    __tablename__ = 'exams'

    id = Column(Integer, primary_key=True)
    description = Column(String(64))


class Result(Base):
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True)
    idperson = Column(Integer,
                      ForeignKey('persons.id', ondelete='CASCADE'),
                      nullable=False)
    idexam = Column(Integer, ForeignKey('exams.id', ondelete='CASCADE'),
                    nullable=False)
    vote = Column(Integer)

    person = relationship('Person')
    exam = relationship('Exam')


if len(sys.argv) == 2 and sys.argv[1] == 'setup':
    url = 'sqlite:////tmp/testdbloady.sqlite'
    e = create_engine(url)
    # Use an explicit creation order to get a stable dump
    Person.__table__.create(e)
    Exam.__table__.create(e)
    Result.__table__.create(e)
