# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Test model
# :Created:   mar 15 nov 2016 14:13:56 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

import sys

from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class Number(Base):
    __tablename__ = 'numbers'

    id = Column(Integer, primary_key=True)
    absolute = Column(Integer)


if len(sys.argv) == 2:
    url = 'sqlite:////tmp/testdbloady.sqlite'
    e = create_engine(url)

    if sys.argv[1] == 'setup':
        Base.metadata.create_all(e)
    elif sys.argv[1] == 'test':
        smaker = sessionmaker(autoflush=False, autocommit=False, bind=e)
        session = smaker()

        assert session.query(Number).get(1).absolute == 1
        assert session.query(Number).get(2).absolute == 2
        assert session.query(Number).get(3).absolute == 2
