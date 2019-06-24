# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Property based attributes test
# :Created:   mer 07 giu 2017 14:15:41 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Lele Gaifax
#

import sys

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class PersonTP(Base):
    __tablename__ = 'persons_tp'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(64))
    lastname = Column(String(64))

    @property
    def fullname(self):
        return self.firstname + ' ' + self.lastname

    @fullname.setter
    def fullname(self, value):
        self.firstname, self.lastname = value.split()


class PersonHP(Base):
    __tablename__ = 'persons_hp'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(64))
    lastname = Column(String(64))

    @hybrid_property
    def fullname(self):
        return self.firstname + ' ' + self.lastname

    @fullname.setter
    def fullname(self, value):
        self.firstname, self.lastname = value.split()


url = 'sqlite:////tmp/testdbloady.sqlite'
e = create_engine(url)

if len(sys.argv) == 2:
    if sys.argv[1] == 'setup':
        Base.metadata.create_all(e)
    elif sys.argv[1] == 'test':
        smaker = sessionmaker(autoflush=False, autocommit=False, bind=e)
        session = smaker()

        person = session.query(PersonTP).one()
        assert person.fullname == 'John Doe'
        assert person.firstname == 'John'
        assert person.lastname == 'Doe'

        person = session.query(PersonHP).one()
        assert person.fullname == 'John Doe'
        assert person.firstname == 'John'
        assert person.lastname == 'Doe'
