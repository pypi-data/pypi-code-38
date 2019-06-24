# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Test model
# :Created:   gio 14 gen 2016 11:30:16 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import sys

from sqlalchemy import create_engine, Column, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    description = Column(String(64))
    starttime = Column(Time())
    endtime = Column(Time())


url = 'sqlite:////tmp/testdbloady.sqlite'
e = create_engine(url)

if len(sys.argv) == 2:
    if sys.argv[1] == 'setup':
        Base.metadata.create_all(e)
    elif sys.argv[1] == 'test':
        smaker = sessionmaker(autoflush=False, autocommit=False, bind=e)
        session = smaker()

        event = session.query(Event).one()
        assert event.description == 'First event'
        assert str(event.starttime) == '12:23:00'
        assert str(event.endtime) == '15:34:00'
