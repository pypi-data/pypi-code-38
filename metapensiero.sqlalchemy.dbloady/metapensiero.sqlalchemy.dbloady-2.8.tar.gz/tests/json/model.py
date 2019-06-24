# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Test model
# :Created:   mar 08 nov 2016 09:50:08 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

import sys

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    attributes = Column(JSONB)


url = 'postgresql://localhost/testdbloady'
e = create_engine(url)

if len(sys.argv) == 2:
    if sys.argv[1] == 'setup':
        Base.metadata.create_all(e)
    elif sys.argv[1] == 'test':
        smaker = sessionmaker(autoflush=False, autocommit=False, bind=e)
        session = smaker()

        all_products = session.query(Product).order_by(Product.name).all()
        assert len(all_products) == 3
        p1 = all_products[0]
        assert p1.name == 'First'
        assert p1.attributes['color'] == 'Black'
        assert p1.attributes['info']['made_by'] == 'Lele'
        p2 = all_products[1]
        assert p2.name == 'Second'
        assert p2.attributes['color'] == 'White'
        assert p2.attributes['info']['made_by'] == 'Roald'
        assert p2.attributes['info']['alt_prod_id'] == p1.id
        p3 = all_products[2]
        assert p3.name == 'Third'
        assert p3.attributes['other_two'] == [p1.id, p2.id]
