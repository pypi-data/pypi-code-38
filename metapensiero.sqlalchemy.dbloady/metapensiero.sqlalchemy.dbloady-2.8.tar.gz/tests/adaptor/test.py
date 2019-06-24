# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Adaptor test
# :Created:   sab 09 gen 2016 11:11:05 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from metapensiero.sqlalchemy.dbloady.load import load
from model import Base, Person, Result


def tweak_data(cls, key, data):
    if cls is Person:
        data['username'] = data['firstname'][:1] + data['lastname']
    elif cls is Result:
        data['vote'] = data['vote'] * 2
    return data


def main():
    e = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(e)

    smaker = sessionmaker(autoflush=False, autocommit=False, bind=e)
    session = smaker()

    load('data.yaml', session, adaptor=tweak_data)

    jdoe = session.query(Person).filter(Person.username == 'JDoe').first()

    assert jdoe.firstname == 'John'
    assert len(jdoe.results) == 1
    assert jdoe.results[0].vote == 20


if __name__ == '__main__':
    main()
