# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Cities model
# :Created:   lun 24 giu 2019 18:24:34 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2019 Lele Gaifax
#

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Cities(Base):
    __tablename__ = 'cities'

    code = Column(String(64), primary_key=True)
    name = Column(String(64))
    country = Column(String(64))
    population = Column(String())
