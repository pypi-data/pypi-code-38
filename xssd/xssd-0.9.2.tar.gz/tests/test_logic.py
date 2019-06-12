#!/usr/bin/python

from base_tests import BaseFileTest
from xssd.errors import *

class SimpleTest(BaseFileTest):
    """Simple Boolean Logic"""
    definition = {
      'root': [{ 'name': 'data', 'type': 'book'}],
      'complexTypes': { 'book': [
        { 'name': 'title' },
        [
           {'name': 'author'},
           [
             {'name': 'writer'},
             {'name': 'artist'},
           ]
        ],
      ] }
    }

    def test_01_author(self):
        """Author and Title"""
        data = { 'data': {'title': 'Foo', 'author': 'Bar'} }
        self.positive_test(data)

    def test_02_writer(self):
        """Writer and Title"""
        data = { 'data': {'title': 'Foo', 'writer': 'Bar', 'artist': 'Baz'} }
        self.positive_test(data)

    def test_03_neither(self):
        """Only the Title"""
        data = { 'data': {'title': 'None'}}
        errors = {'artist': INVALID_REQUIRED, 'writer': INVALID_REQUIRED, 'author': INVALID_REQUIRED, 'title': NO_ERROR}
        self.negative_test(data, {'data': errors})

    def test_04_not_enough(self):
        """Writer without Artist"""
        data = { 'data': {'title': 'None', 'artist': 'Baz'}}
        errors = {'artist': NO_ERROR, 'writer': INVALID_REQUIRED, 'author': INVALID_REQUIRED, 'title': NO_ERROR}
        self.negative_test(data, {'data': errors})

    def test_05_not_enough_writer(self):
        """Artist without Writer"""
        data = { 'data': {'title': 'None', 'writer': 'Bar'}}
        errors = {'artist': INVALID_REQUIRED, 'writer': NO_ERROR, 'author': INVALID_REQUIRED, 'title': NO_ERROR}
        self.negative_test(data, {'data': errors})



class BooleanTest(BaseFileTest):
    """This tests boolean exists logic"""
    definition = {
      'root': [{ 'name': 'data', 'type': 'article', 'maxOccurs': 4 }],

      'complexTypes': { 'article': [ [
        # The double array turns the logic from AND to OR
        { 'name': 'title', 'type': 'string' },
        [ # The third array turns it back to AND
          { 'name': 'name',   'type': 'string' },
          { 'name': 'author', 'type': 'string' },
        ],[
          { 'name': 'name',   'type': 'string' },
          { 'name': 'editor', 'type': 'string' },
          [ # The forth goes back to OR
            { 'name': 'author', 'type': 'string' },
            { 'name': 'title', 'type': 'string' },
          ]
        ] ] ],
      },
    }

    def test_01_combination(self):
        """Single Item Structure"""
        data = {'data': [ { 'title': 'Correct News' } ] }
        self.positive_test(data)

    def test_02_name_author(self):
        """Double Item Structure"""
        data = {'data': [ { 'name' : 'Correct News', 'author': 'This guy I Know' } ] }
        self.positive_test(data)

    def test_03_author_editor(self):
        """Third Iterator First"""
        data = {'data': [ { 'name' : 'Correct News', 'editor': 'Blah', 'author': 'This guy I Know' } ] }
        self.positive_test(data)

    def test_04_title_editor(self):
        """Third Iterator Second"""
        data = {'data': [ { 'name' : 'Correct News', 'editor': 'Blah', 'title': 'Fore Bare' } ] }
        self.positive_test(data)

    def test_21_first_fail(self):
        """Missing Title"""
        data = {'data': [ { 'author': 'This guy' } ] }
        errors = { 'data': [ {
            'title'  : INVALID_REQUIRED,
            'name'   : INVALID_REQUIRED,
            'editor' : INVALID_REQUIRED,
            'author' : NO_ERROR,
        } ] }
        self.negative_test(data, errors)

    def test_22_second_fail(self):
        """Missing Name"""
        data = {'data': [ { 'name': 'This guy' } ] }
        errors = { 'data': [ {
            'title'  : INVALID_REQUIRED,
            'name'   : NO_ERROR,
            'editor' : INVALID_REQUIRED,
            'author' : INVALID_REQUIRED,
        } ] }
        self.negative_test(data, errors)

    def test_23_third_fail(self):
        """Missing Editor Choice"""
        data = {'data': [ { 'name': 'This guy', 'editor': 'foo',  } ] }
        errors = { 'data': [ {
            'title'  : INVALID_REQUIRED,
            'name'   : NO_ERROR,
            'editor' : NO_ERROR,
            'author' : INVALID_REQUIRED,
        } ] }
        self.negative_test(data, errors)

if __name__ == '__main__':
    import unittest
    unittest.main()
