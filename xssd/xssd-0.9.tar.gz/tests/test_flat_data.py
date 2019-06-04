#!/usr/bin/python

from base_tests import BaseFileTest
from xssd.errors import *

class FlatDataTest(BaseFileTest):
    """Test checking what happens with simple types in the root."""
    definition = {
      'root' : [
        { 'name' : 'title',   'type' : 'string', 'maxLength' : 25 },
        { 'name' : 'content', 'type' : 'string', 'minLength' : 22 },
        { 'name' : 'author',  'type' : 'token',  'maxLength' : 54 },
        { 'name' : 'editor',  'type' : 'token',  'minOccurs' : 0 },
        { 'name' : 'created', 'type' : 'datetime' },
        { 'name' : 'edited',  'type' : 'datetime', 'maxOccurs' : 3 },
      ],
    }

    def test_correct(self):
        """Flat Data is Acceptable"""
        # Odd should pass, Even should fail.
        data = {
          'title'   : 'Correct News',
          'content' : 'This content should always be above 20 charters in length.',
          'author'  : 'mowens',
          'created' : '2007-11-09 20:23:12',
          'edited' : '2007-11-09 20:23:12',
        }
        self.positive_test(data)

    def test_negative(self):
        """Flat Data is Unacceptable"""
        data = {
          'title'   : 'Bad News which has a title which is way too long for this validation to work.',
          'content' : 'Too Short',
          'editor'  : [ 'token1', 'token2' ],
          'created' : '2008-11-09 20:23:12',
          'edited'  : [ '2007-11-09 20:23:12', '2007-11-09 20:23:12', '2007-11-09 20:23:12', '2007-11-09 20:23:12' ],
        }
        errors = {
          'created' : NO_ERROR,
          'editor'  : INVALID_MAX_OCCURS,
          'content' : INVALID_MINLENGTH,
          'title'   : INVALID_MAXLENGTH,
          'edited'  : INVALID_MAX_OCCURS,
          'author'  : INVALID_REQUIRED,
        }
        self.negative_test(data, errors)

