# encoding: utf-8

from __future__ import unicode_literals

import pytest

from web.core.context import Context
from web.db.sa import SQLAlchemyConnection

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Person(Base):
	__tablename__ = 'person'
	id = Column(Integer, primary_key=True)
	name = Column(String)


class Address(Base):
	__tablename__ = 'address'
	id = Column(Integer, primary_key=True)
	address = Column(String)
	person_id = Column(Integer, ForeignKey(Person.id))
	person = relationship(Person)


@pytest.fixture
def sa():
	ctx = Context(db=Context())
	sa = SQLAlchemyConnection('sqlite://', 'test')
	
	sa.start(ctx)
	engine = ctx.db.test
	
	sa.prepare(ctx)
	session = ctx.db.test
	
	yield engine, session
	
	sa.done(ctx)
	sa.stop(ctx)


class TestSQLAlchemy(object):
	def test_lifecycle(self, sa):
		pass
	
	def test_repr(self):
		sa = SQLAlchemyConnection('sqlite://', 'test')
		assert repr(sa) == 'SQLAlchemyConnection(test, "sqlite://")'
	
	def test_use(self, sa):
		engine, session = sa
		
		Base.metadata.create_all(engine)
		
		p = Person(name='person')
		session.add(p)
		
		a = Address(address='address', person=p)
		session.add(a)
		
		session.commit()
		
		p = session.query(Person).filter(Person.name == 'person').one()
		assert isinstance(p, Person)
		assert p.id == 1

