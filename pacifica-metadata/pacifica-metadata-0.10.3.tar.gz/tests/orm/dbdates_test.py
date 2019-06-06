#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Base testing module implements the temporary database to be used."""
from datetime import datetime, timedelta
from time import mktime
from json import dumps
from pacifica.metadata.orm.utils import datetime_now_nomicrosecond
from pacifica.metadata.orm.base import PacificaModel
from .base_test import TestBase

SAMPLE_ZERO_ISO_HASH = {
    'created': '1969-12-31T16:00:00',
    'updated': '1969-12-31T16:00:00',
    'deleted': '1969-12-31T16:00:00'
}
SAMPLE_ZERO_HASH = {
    'created': 0,
    'updated': 0,
    'deleted': None
}
SAMPLE_REP_HASH = {
    'created': datetime_now_nomicrosecond().isoformat(),
    'updated': datetime_now_nomicrosecond().isoformat(),
    'deleted': None
}
SAMPLE_BAD_HASH = {
    'created': 'blarg',
    'updated': int(mktime(datetime.utcnow().timetuple())),
    'deleted': None
}


class TestDBDates(TestBase):
    """Setup the test cases for the base object attributes for the ORM."""

    obj_cls = PacificaModel
    # pylint: disable=no-member
    obj_id = PacificaModel.id
    # pylint: enable=no-member

    @classmethod
    def dependent_cls(cls):
        """Return dependent classes for the base model object."""
        return [PacificaModel]

    def test_bad_dates_from_hash(self):
        """Test method to check the hash against zero dates."""
        exception_str = 'unknown string format'
        try:
            self.base_test_hash(SAMPLE_BAD_HASH)
        except ValueError as ex:
            self.assertTrue(exception_str in str(ex).lower())
        try:
            self.base_test_json('["foo"]')
        except ValueError as ex:
            self.assertEqual(str(ex), 'json_str not dict')

    def test_zero_dates_from_hash(self):
        """Test method to check the hash against zero dates."""
        self.base_test_hash(SAMPLE_ZERO_ISO_HASH)

    def test_zero_dates_from_json(self):
        """Test method to check the json against zero dates."""
        self.base_test_json(dumps(SAMPLE_ZERO_ISO_HASH))

    def test_zero_dates_from_where(self):
        """Test method to check the where clause against zero dates."""
        self.base_where_clause(SAMPLE_ZERO_ISO_HASH)

    def test_now_dates_from_hash(self):
        """Test method to check the hash against now dates."""
        self.base_test_hash(SAMPLE_REP_HASH)

    def test_now_dates_from_json(self):
        """Test method to check the json against now dates."""
        self.base_test_json(dumps(SAMPLE_REP_HASH))

    def test_now_dates_from_where(self):
        """Test method to check the where clause against now dates."""
        self.base_where_clause(SAMPLE_REP_HASH)

    def test_dates_range(self):
        """Test date ranges using operators."""
        self.base_create_obj(PacificaModel, SAMPLE_REP_HASH)
        self.base_create_obj(PacificaModel, SAMPLE_ZERO_ISO_HASH)
        third_obj = PacificaModel()
        date_check_max = datetime.utcnow() + timedelta(minutes=1)
        date_check_min = datetime.utcnow() - timedelta(minutes=15)
        search_expr = {
            'created': date_check_max.replace(microsecond=0).isoformat(),
            'created_operator': 'LT'
        }
        objs = self.base_where_clause_search(third_obj, search_expr)
        self.assertEqual(len(objs), 2)
        search_expr = {
            'created': '0',
            'created_0': date_check_min.replace(microsecond=0).isoformat(),
            'created_1': date_check_max.replace(microsecond=0).isoformat(),
            'created_operator': 'BETWEEN'
        }
        objs = self.base_where_clause_search(third_obj, search_expr)
        self.assertEqual(len(objs), 1)

    def test_null_dates_and_query(self):
        """Test method to check that null deleted dates work."""
        where_hash_null = {
            'deleted': None
        }
        where_hash_not_null = {
            'deleted': SAMPLE_ZERO_ISO_HASH['deleted']
        }
        self.base_create_obj(PacificaModel, SAMPLE_REP_HASH)
        self.base_create_obj(PacificaModel, SAMPLE_ZERO_ISO_HASH)
        third_obj = PacificaModel()
        expr = third_obj.where_clause(where_hash_null)
        null_chk_obj = third_obj.get(expr)
        chk_obj_hash = null_chk_obj.to_hash()
        self.assertTrue(chk_obj_hash['deleted'] is None)
        expr = third_obj.where_clause(where_hash_not_null)
        not_null_chk_obj = third_obj.get(expr)
        chk_obj_hash = not_null_chk_obj.to_hash()
        self.assertFalse(chk_obj_hash['deleted'] is None)

    def test_bool_translate(self):
        """Test the bool translate method."""
        # pylint: disable=protected-access
        self.assertTrue(PacificaModel._bool_translate(True))
        self.assertFalse(PacificaModel._bool_translate('False'))
        self.assertFalse(PacificaModel._bool_translate('false'))
        # pylint: enable=protected-access
