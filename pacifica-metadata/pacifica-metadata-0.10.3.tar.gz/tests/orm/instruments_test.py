#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the instruments ORM object."""
from json import dumps
from pacifica.metadata.orm.instruments import Instruments
from .base_test import TestBase

SAMPLE_INSTRUMENT_HASH = {
    '_id': 1234,
    'name': 'My Really Long Winded Instrument Name',
    'display_name': 'My Instrument Name',
    'name_short': 'Instrument',
    'active': True,
    'encoding': 'UTF8'
}

SAMPLE_UNICODE_INSTRUMENT_HASH = {
    '_id': 1234,
    'name': u'My Really Long Winded Instrumént Name',
    'display_name': u'My Instrument Namé',
    'name_short': u'Instrumént',
    'encoding': 'UTF8'
}


class TestInstruments(TestBase):
    """Test the Instruments ORM object."""

    obj_cls = Instruments
    obj_id = Instruments.id

    def test_instruments_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_INSTRUMENT_HASH)

    def test_unicode_instruments_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_UNICODE_INSTRUMENT_HASH)

    def test_instruments_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_INSTRUMENT_HASH))

    def test_instruments_sexpr_uni(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_UNICODE_INSTRUMENT_HASH,
            name_operator='ILIKE',
            name=u'%é%'
        )

    def test_instruments_sexpr_txt(self):
        """Test the hash portion using base object method."""
        self.base_where_clause_search_expr(
            SAMPLE_INSTRUMENT_HASH,
            name_operator='ILIKE',
            name='My%'
        )

    def test_instruments_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_INSTRUMENT_HASH)

    def test_unicode_instruments_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_UNICODE_INSTRUMENT_HASH)
