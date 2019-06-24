# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Test model
# :Created:   gio 22 ott 2015 18:07:50 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2015, 2016, 2017 Lele Gaifax
#

import sys

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    description = Column(HSTORE)


class Attribute(Base):
    __tablename__ = 'attributes'

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    description = Column(HSTORE)


class Values(Base):
    __tablename__ = 'product_attributes'

    id = Column(Integer, primary_key=True)
    idproduct = Column(Integer,
                       ForeignKey('products.id', ondelete='CASCADE'),
                       nullable=False)
    idattribute = Column(Integer, ForeignKey('attributes.id', ondelete='CASCADE'),
                         nullable=False)
    value = Column(String(64))

    product = relationship('Product')
    attribute = relationship('Attribute')


url = 'postgresql://localhost/testdbloady'
e = create_engine(url)

if len(sys.argv) == 2:
    if sys.argv[1] == 'setup':
        Base.metadata.create_all(e)
    else:
        smaker = sessionmaker(autoflush=False, autocommit=False, bind=e)
        session = smaker()

        if sys.argv[1] == 'test_1':
            all_values = session.query(Values).order_by(Values.value).all()
            assert len(all_values) == 3
            v = all_values[0]
            assert v.product.description['en'] == 'Roadrunner cage'
            assert v.product.description['it'] == 'Gabbia per struzzi'
            assert v.attribute.description['en'] == 'Size'
            assert v.attribute.description['it'] == 'Dimensione'
            v = all_values[1]
            assert v.value == '230kg'
            assert v.attribute.description['en'] == 'Weight'
            assert v.attribute.description['it'] == 'Peso'
            v = all_values[2]
            assert v.value == 'Box'
            assert v.attribute.description['en'] == 'Aspect'
            assert v.attribute.description['it'] == 'Aspetto'
        elif sys.argv[1] == 'test_2':
            assert session.query(Product).all() == []
            assert session.query(Attribute).all() == []
            assert session.query(Values).all() == []
