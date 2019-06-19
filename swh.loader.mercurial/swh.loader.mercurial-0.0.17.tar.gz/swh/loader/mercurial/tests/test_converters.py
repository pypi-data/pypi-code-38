# Copyright (C) 2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import unittest

from swh.loader.mercurial import converters


class TestParseAuthorConverters(unittest.TestCase):
    def test_parse_author_no_email(self):
        self.assertIsNone(converters.parse_author(None))

    def test_parse_author_no_bracket(self):
        actual_author = converters.parse_author(b'someone')

        self.assertEqual(actual_author, {
            'name': None,
            'email': None,
            'fullname': b'someone'
        })

    def test_parse_author_2(self):
        actual_author = converters.parse_author(b'something <wicked')

        self.assertEqual(actual_author, {
            'name': b'something',
            'email': None,
            'fullname': b'something <wicked'
        })

    def test_parse_author_3(self):
        actual_author = converters.parse_author(b'something >wicked')

        self.assertEqual(actual_author, {
            'name': None,
            'email': None,
            'fullname': b'something >wicked'
        })

    def test_parse_author_4(self):
        actual_author = converters.parse_author(b'something <')

        self.assertEqual(actual_author, {
            'name': b'something',
            'email': None,
            'fullname': b'something <'
        })

    def test_parse_author_5(self):
        actual_author = converters.parse_author(b'<only>')

        self.assertEqual(actual_author, {
            'name': None,
            'email': b'only',
            'fullname': b'<only>'
        })

    def test_parse_author_6(self):
        actual_author = converters.parse_author(b'  <something>')

        self.assertEqual(actual_author, {
            'name': b' ',
            'email': b'something',
            'fullname': b'  <something>'
        })

    def test_parse_author_normal(self):
        actual_author = converters.parse_author(b'someone <awesome>')

        self.assertEqual(actual_author, {
            'name': b'someone',
            'email': b'awesome',
            'fullname': b'someone <awesome>'
        })
