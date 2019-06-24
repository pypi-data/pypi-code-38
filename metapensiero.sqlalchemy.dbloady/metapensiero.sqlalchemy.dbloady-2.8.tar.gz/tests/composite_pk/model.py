# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Test model
# :Created:   lun 14 nov 2016 23:47:27 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

import sys

from sqlalchemy import (create_engine, Column, ForeignKey, ForeignKeyConstraint,
                        Integer, Sequence, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()

class Country(Base):
    __tablename__ = 'countries'

    id = Column(String(2), primary_key=True, nullable=False)
    name = Column(String(64), nullable=False)


class City(Base):
    __tablename__ = 'cities'

    country_id = Column(String(2), ForeignKey('countries.id'),
                        primary_key=True, nullable=False)
    code = Column(String(4), primary_key=True, nullable=False)
    name = Column(String(64), nullable=False)

    country = relationship('Country')

class Address(Base):
    __tablename__ = 'addresses'
    __table_args__ = (
        ForeignKeyConstraint(['country_id', 'city_code'],
                             ['cities.country_id', 'cities.code']),
    )

    id = Column(Integer, Sequence('address_id_seq'), primary_key=True)
    country_id = Column(String(2), ForeignKey('countries.id'),
                        nullable=True)
    city_code = Column(String(4), nullable=True)
    street = Column(String(64), nullable=False)

    country = relationship('Country')
    city = relationship('City',
                        primaryjoin=
                        "and_(City.code == foreign(Address.city_code),"
                        "City.country_id == Address.country_id)")

if len(sys.argv) == 2:
    url = 'sqlite:////tmp/testdbloady.sqlite'
    e = create_engine(url)

    if sys.argv[1] == 'setup':
        Base.metadata.create_all(e)
    elif sys.argv[1] == 'test':
        smaker = sessionmaker(autoflush=False, autocommit=False, bind=e)
        session = smaker()

        addresses = session.query(Address).order_by(Address.city_code).all()
        assert len(addresses) == 2
