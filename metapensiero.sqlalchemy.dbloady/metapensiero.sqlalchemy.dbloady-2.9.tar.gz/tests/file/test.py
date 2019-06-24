# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- File test
# :Created:   dom 08 apr 2018 13:59:56 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from metapensiero.sqlalchemy.dbloady.load import load
from model import Base, Content


def main():
    e = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(e)

    smaker = sessionmaker(autoflush=False, autocommit=False, bind=e)
    session = smaker()

    load('data.yaml', session)

    content = session.query(Content).get('€')

    assert content.content == 'a' * 100
    assert content.binary == b'binary.bin'
    assert ':Copyright: © 2018' in content.script


if __name__ == '__main__':
    main()
