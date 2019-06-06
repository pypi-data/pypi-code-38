#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module tests the specific class method from PacificaModel.

Specifically, available_hash_list and get_primary_keys from
PacificaModel since they both require primary
keys and the PacificaModel doesn't have any...
"""
from pacifica.metadata.orm.keys import Keys
from pacifica.metadata.orm.user_group import UserGroup
from .base_test import TestBase


class TestKeysHashList(TestBase):
    """Test the available hash with sample keys."""

    def test_primary_keys_with_keys(self):
        """Test the method to check primary keys with Keys."""
        check_list = Keys.get_primary_keys()
        self.assertTrue(isinstance(check_list, list))
        self.assertTrue(len(check_list) == 1)
        self.assertTrue('id' in check_list)

    def test_primary_keys_user_group(self):
        """Test the primary keys method with user group."""
        check_list = UserGroup.get_primary_keys()
        self.assertTrue(isinstance(check_list, list))
        self.assertTrue(len(check_list) == 2)
        self.assertTrue('person' in check_list)
        self.assertTrue('group' in check_list)

    def test_hash_list_with_keys(self):
        """Test method to check the results of available hash list."""
        sample_key1 = {
            '_id': 127,
            'key': 'Test Key 1',
            'encoding': 'UTF8'
        }
        sample_key2 = {
            '_id': 128,
            'key': 'Test Key 2',
            'encoding': 'UTF8'
        }
        sample_key3 = {
            '_id': 130,
            'key': 'Test Key 3',
            'encoding': 'UTF8'
        }
        self.base_create_obj(Keys, sample_key1)
        self.base_create_obj(Keys, sample_key2)
        self.base_create_obj(Keys, sample_key3)
        third_obj = Keys()
        hash_list, hash_dict = third_obj.available_hash_list()
        self.assertTrue(len(hash_list) == 3)
        # some sanity checking for the layout of the two objects
        for hashed_key in hash_list:
            self.assertTrue(hashed_key in hash_dict)
            obj_key_meta = hash_dict[hashed_key]
            self.assertTrue('index_hash' in obj_key_meta)
            self.assertTrue('key_list' in obj_key_meta)
            self.assertTrue('id' in obj_key_meta['key_list'])
            self.assertTrue(hashed_key == obj_key_meta['index_hash'])
