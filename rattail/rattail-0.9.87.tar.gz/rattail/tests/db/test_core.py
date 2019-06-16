# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

from rattail.db import core


class TestCore(TestCase):

    def test_uuid_column(self):
        column = core.uuid_column()
        self.assertTrue(isinstance(column, Column))
        self.assertEqual(column.name, None)
        self.assertTrue(column.primary_key)
        self.assertFalse(column.nullable)
        self.assertFalse(column.default is None)

    def test_uuid_column_no_default(self):
        column = core.uuid_column(default=None)
        self.assertTrue(column.default is None)

    def test_uuid_column_nullable(self):
        column = core.uuid_column(nullable=True)
        self.assertTrue(column.nullable)


class TestGetSetFactory(TestCase):

    def setUp(self):
        Base = declarative_base()

        class Primary(Base):
            __tablename__ = 'primary'
            id = Column(Integer(), primary_key=True)
            foo = Column(String(length=10))

        class Secondary(Base):
            __tablename__ = 'secondary'
            id = Column(Integer(), primary_key=True)
            primary_id = Column(Integer(), ForeignKey('primary.id'))
            bar = Column(String(length=10))

        Primary._secondary = relationship(
            Secondary, backref='primary', uselist=False)
        Primary.bar = association_proxy(
            '_secondary', 'bar',
            getset_factory=core.getset_factory)

        self.Primary = Primary
        self.Secondary = Secondary
        
        engine = create_engine('sqlite://')
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def tearDown(self):
        self.session.close()

    def test_getter_returns_none_if_proxy_value_is_absent(self):
        p = self.Primary()
        self.session.add(p)
        self.assertTrue(p.bar is None)

    def test_getter_returns_proxy_value_if_proxy_value_is_present(self):
        p = self.Primary()
        self.assertTrue(p.bar is None)
        s = self.Secondary(primary=p, bar='something')
        self.session.add(p)
        self.assertEqual(p.bar, 'something')

    def test_setter_assigns_proxy_value(self):
        p = self.Primary()
        s = self.Secondary(primary=p)
        self.session.add(p)
        self.assertTrue(s.bar is None)
        p.bar = 'something'
        self.assertEqual(s.bar, 'something')
