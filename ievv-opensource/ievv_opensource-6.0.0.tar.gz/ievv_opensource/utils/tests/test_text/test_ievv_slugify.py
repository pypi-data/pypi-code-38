# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase

from ievv_opensource.utils.text.ievv_slugify import ievv_slugify


class TestIevvSlugify(TestCase):
    def test_ievv_slugify_e(self):
        self.assertEqual('a', ievv_slugify("æ"))

    def test_ievv_slugify_o(self):
        self.assertEqual('o', ievv_slugify("ø"))

    def test_ievv_slugify_a(self):
        self.assertEqual('a', ievv_slugify("å"))

    def test_ievv_slugify_word(self):
        self.assertEqual('halla-assen-gare-a-do', ievv_slugify('Hællæ Åssen gåre æ dø!'))

    def test_ievv_slugify_word_with_settings_map(self):
        character_replace_map = {
            'æ': 'ae',
            'ø': 'oe',
            'å': 'aa'
        }
        with self.settings(IEVV_SLUGIFY_CHARACTER_REPLACE_MAP=character_replace_map):
            self.assertEqual('haellae-assen-gaare-ae-doe', ievv_slugify('Hællæ Åssen gåre æ dø!'))
