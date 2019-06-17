# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import
import os
import os.path
from io import open

from nose.tools import assert_equal, assert_not_equal
from nose import SkipTest

from pypeline.markup import markup
from pypeline.markup import ALLOWED_TAGS, ALLOWED_ATTRIBUTES, ALLOWED_STYLES
from pypeline.tests import TestPairwise
import six

from unittest import TestCase
TestCase.maxDiff = None

class TestMarkup(TestPairwise):

    basedir = os.path.join(os.path.dirname(__file__), 'markups')

    """
    test_* methods are run like regular tests
    _test_* methods are run with the allpairs logic (e.g. once for each readme)
        and that is kicked off by test()
    """
    def __init__(self):
        super(TestMarkup, self).__init__()
        self.data = {}
        files = os.listdir(self.basedir)
        for f in files:
            format = os.path.splitext(f)[1].lstrip('.')
            if format == 'html':
                continue
            self.data[format] = f

    def setUp(self):
        pass

    def _test_rendering(self, format):
        if format not in markup.markups_names and format != 'plaintext':
            raise SkipTest()
        readme = self.data[format]
        source_file = open(os.path.join(self.basedir, readme), 'r', encoding='utf-8')
        source = source_file.read()
        expected_file = open(os.path.join(self.basedir, '%s.html' % readme),
                             'r', encoding='utf-8')
        expected = expected_file.read()
        actual = markup.render(os.path.join(self.basedir, readme))
        #assert_true(isinstance(actual, unicode))
        if source != expected:
            assert_not_equal(source, actual, "Did not render anything.")
        assert_equal(expected, actual)

    def test_can_render(self):
        assert_equal(None, markup.can_render('README.cmd'))
        if 'markdown' not in markup.markups_names:
            raise SkipTest()
        else:
            assert_equal('markdown', markup.can_render('README.markdown'))
            assert_equal('markdown', markup.can_render('README.md'))

    def test_unicode_utf8(self):
        chinese = markup.unicode('華語')
        assert_equal(chinese, '華語')
        assert_equal(type(chinese), six.text_type)

    def test_unicode_ascii(self):
        ascii = markup.unicode('abc')
        assert_equal(ascii, 'abc')
        assert_equal(type(ascii), six.text_type)

    def test_unicode_latin1(self):
        latin1 = 'abcdé'.encode('latin_1')
        latin1 = markup.unicode(latin1)
        assert_equal(latin1, 'abcdé')
        assert_equal(type(latin1), six.text_type)


class TestHTMLAllowedValues(object):

    def test_ALLOWED_TAGS(self):
        assert 'pre' in ALLOWED_TAGS
        assert 'button' not in ALLOWED_TAGS
        assert 'glyph' not in ALLOWED_TAGS  # svg

    def test_ALLOWED_ATTRIBUTES(self):
        assert 'alt' in ALLOWED_ATTRIBUTES['*']
        assert 'clip-path' not in ALLOWED_ATTRIBUTES['*']  # svg

    def test_ALLOWED_STYLES(self):
        assert 'color' in ALLOWED_STYLES
        assert 'position' not in ALLOWED_STYLES
        assert '-moz-binding' not in ALLOWED_STYLES