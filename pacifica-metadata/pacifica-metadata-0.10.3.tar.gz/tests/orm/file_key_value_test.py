#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the file_key_values ORM object."""
from json import dumps
from pacifica.metadata.orm.file_key_value import FileKeyValue
from pacifica.metadata.orm.files import Files
from pacifica.metadata.orm.keys import Keys
from pacifica.metadata.orm.values import Values
from .base_test import TestBase
from .files_test import SAMPLE_FILE_HASH, TestFiles
from .keys_test import SAMPLE_KEY_HASH, TestKeys
from .values_test import SAMPLE_VALUE_HASH, TestValues

SAMPLE_FILE_KEY_VALUE_HASH = {
    'file': SAMPLE_FILE_HASH['_id'],
    'key': SAMPLE_KEY_HASH['_id'],
    'value': SAMPLE_VALUE_HASH['_id']
}


class TestFileKeyValue(TestBase):
    """Test the Keys ORM object."""

    obj_cls = FileKeyValue
    obj_id = FileKeyValue.file

    @classmethod
    def base_create_dep_objs(cls):
        """Create all objects that FileKeyValue need."""
        keys = Keys()
        TestKeys.base_create_dep_objs()
        keys.from_hash(SAMPLE_KEY_HASH)
        keys.save(force_insert=True)
        values = Values()
        TestValues.base_create_dep_objs()
        values.from_hash(SAMPLE_VALUE_HASH)
        values.save(force_insert=True)
        files = Files()
        TestFiles.base_create_dep_objs()
        files.from_hash(SAMPLE_FILE_HASH)
        files.save(force_insert=True)

    def test_file_key_value_hash(self):
        """Test the hash portion using base object method."""
        self.base_test_hash(SAMPLE_FILE_KEY_VALUE_HASH)

    def test_file_key_value_json(self):
        """Test the hash portion using base object method."""
        self.base_test_json(dumps(SAMPLE_FILE_KEY_VALUE_HASH))

    def test_file_key_value_where(self):
        """Test the hash portion using base object method."""
        self.base_where_clause(SAMPLE_FILE_KEY_VALUE_HASH)
