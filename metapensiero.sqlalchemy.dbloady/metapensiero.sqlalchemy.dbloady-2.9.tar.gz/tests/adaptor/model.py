# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Test model
# :Created:   sab 09 gen 2016 10:55:39 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Person(Base):
    __tablename__ = 'persons'

    username = Column(String(64), primary_key=True)
    firstname = Column(String(64))
    lastname = Column(String(64))


class Exam(Base):
    __tablename__ = 'exams'

    id = Column(Integer, primary_key=True)
    description = Column(String(64))


class Result(Base):
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True)
    username = Column(Integer,
                      ForeignKey('persons.username', ondelete='CASCADE'),
                      nullable=False)
    idexam = Column(Integer, ForeignKey('exams.id', ondelete='CASCADE'),
                    nullable=False)
    vote = Column(Integer)

    person = relationship('Person', backref='results')
    exam = relationship('Exam')
