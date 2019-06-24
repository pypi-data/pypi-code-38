# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- TSV test
# :Created:   lun 24 giu 2019 18:27:40 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2019 Lele Gaifax
#

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from metapensiero.sqlalchemy.dbloady.load import load
from model import Base, Cities


def main():
    e = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(e)

    smaker = sessionmaker(autoflush=False, autocommit=False, bind=e)
    session = smaker()

    load('data.yaml', session)

    city = session.query(Cities).get('H612')

    assert city.name == 'Rovereto'
    assert city.country == 'Italy'
    assert city.population == '39825'

    city = session.query(Cities).get('XXXX')

    assert city.name == '“X”'
    assert city.country == 'X'
    assert city.population is None


if __name__ == '__main__':
    main()
