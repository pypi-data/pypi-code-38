# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- File model
# :Created:   dom 08 apr 2018 13:57:57 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#


from sqlalchemy import Binary, Column, String, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Content(Base):
    __tablename__ = 'contents'

    code = Column(String(64), primary_key=True)
    binary = Column(Binary())
    script = Column(UnicodeText())
    content = Column(UnicodeText())
