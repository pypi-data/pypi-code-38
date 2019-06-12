#!/usr/bin/python

from base_tests import BaseFileTest
from xssd.errors import *

class OccursTest(BaseFileTest):
    """This tests boolean exists logic"""
    definition = {
      'root': [ { 'name': 'data', 'type': 'article', 'minOccurs': 2 } ],
      'complexTypes': {
      'article': [
        { 'name': 'title',   'type': 'string' },
        { 'name': 'content', 'type': 'string', 'minOccurs': 0 },
        { 'name': 'tags',    'type': 'tag',  'minOccurs': 2, 'maxOccurs': '3' },
      ],
      'tag': [
        { 'name': 'name',   'type': 'string' },
        { 'name': 'count',  'type': 'integer' },
      ],
    }}

    def test_03_positive(self):
        """Max and Min Required"""
        data = {'data': [
        {
          'title'  : 'Correct News',
          'content': 'Foo',
          'tags'   : [
            { 'name': 'tag1', 'count': '2' },
            { 'name': 'tag2', 'count': '0' },
          ],
        },
        {
          'title'  : 'Correct News',
          'content': 'Bar',
          'tags'   : [
             { 'name': 'tag3', 'count': '9' },
             { 'name': 'tag2', 'count': '0' },
          ]
        }]}
        self.positive_test(data)

    def test_03_too_few(self):
        """Too Few Items"""
        data = {'data': [
          { 'title': 'This guy', 'tags' : { 'name': 'tag3', 'count': '9' }, },
        ]}
        errors = { 'data': INVALID_MIN_OCCURS }
        self.negative_test(data, errors)

    def test_04_too_many(self):
        """Too Few Items"""
        data = {'data': [
          { 'title': 'This guy', 'tags' : { 'name': 'tag3', 'count': '9' }},
          { 'title': 'This guy', 'tags' : [
            { 'name': 'tag1', 'count': '2' },
            { 'name': 'tag2', 'count': '5' },
            { 'name': 'tag3', 'count': '3' },
            { 'name': 'tag4', 'count': '9' },
          ]}
        ]}
        errors = {'data': [
          {'content': NO_ERROR, 'tags': INVALID_MIN_OCCURS, 'title': NO_ERROR},
          {'content': NO_ERROR, 'tags': INVALID_MAX_OCCURS, 'title': NO_ERROR},
        ]}
        self.negative_test(data, errors)


