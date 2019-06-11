#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports
import unittest

from zope.interface import Interface

from nti.schema.jsonschema import JsonSchemafier

from . import SchemaLayer

from hamcrest import assert_that
from hamcrest import has_entry
from hamcrest import has_item
from hamcrest import has_property
from hamcrest import is_
from hamcrest import is_in
from hamcrest import is_not
from hamcrest import not_none

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904,inherit-non-class


does_not = is_not


class TestConfiguredVocabulary(unittest.TestCase):

    layer = SchemaLayer

    def test_country_vocabulary(self):
        from zope.schema import Choice

        class IA(Interface):
            choice = Choice(title=u"Choice",
                            vocabulary=u"Countries")

        o = object()

        choice = IA['choice'].bind(o)
        assert_that(choice.vocabulary, is_(not_none()))
        assert_that('us', is_in(choice.vocabulary))
        term = choice.vocabulary.getTermByToken('us')
        assert_that(term, has_property('value', "United States"))
        ext = term.toExternalObject()
        assert_that(ext, has_entry('flag', u'/++resource++country-flags/us.gif'))
        assert_that(ext, has_entry('title', 'United States'))

        schema = JsonSchemafier(IA).make_schema()
        assert_that(schema, has_entry('choice', has_entry('choices', has_item(ext))))

def test_suite():
    import doctest
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTest(
        doctest.DocTestSuite("nti.schema.vocabulary")
    )

    return suite
