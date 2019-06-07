# -*- coding:utf-8 -*-
#
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
import sys
if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest
from os import path

from nazca.utils.normalize import (BaseNormalizer, UnicodeNormalizer, JoinNormalizer,
                                   SimplifyNormalizer, TokenizerNormalizer,
                                   LemmatizerNormalizer, RoundNormalizer,
                                   RegexpNormalizer, NormalizerPipeline,
                                   lunormalize, lemmatized,
                                   roundstr, rgxformat, tokenize, simplify)
from nazca.data import FRENCH_LEMMAS


TESTDIR = path.dirname(__file__)


class NormalizerFunctionTestCase(unittest.TestCase):

    def test_unormalize(self):
        self.assertEqual(lunormalize(u'bépoèàÀêùï'),
                         u'bepoeaaeui')

    def test_simplify(self):
        self.assertEqual(simplify(u"J'aime les frites, les pommes et les"
                                  u" scoubidous !", FRENCH_LEMMAS),
                         u"aimer frites pomme scoubidou")

    def test_tokenize(self):
        self.assertEqual(tokenize(u"J'aime les frites !"),
                         [u"J'", u'aime', u'les', u'frites', u'!', ])

    def test_lemmatizer(self):
        self.assertEqual(lemmatized(u'sacré rubert', FRENCH_LEMMAS), u'sacré rubert')
        self.assertEqual(lemmatized(u"J'aime les frites !", FRENCH_LEMMAS),
                         u'je aimer le frite')
        self.assertEqual(lemmatized(u", J'aime les frites", FRENCH_LEMMAS),
                         u'je aimer le frite')

    def test_round(self):
        self.assertEqual(roundstr(3.14159, 2), '3.14')
        self.assertEqual(roundstr(3.14159), '3')
        self.assertEqual(roundstr('3.14159', 3), '3.142')

    def test_format(self):
        string = u'[Victor Hugo - 26 fev 1802 / 22 mai 1885]'
        regex = r'\[(?P<firstname>\w+) (?P<lastname>\w+) - ' \
            r'(?P<birthdate>.*) \/ (?P<deathdate>.*?)\]'
        output = u'%(lastname)s, %(firstname)s (%(birthdate)s - %(deathdate)s)'
        self.assertEqual(rgxformat(string, regex, output),
                         u'Hugo, Victor (26 fev 1802 - 22 mai 1885)')

        string = u'http://perdu.com/42/supertop/cool'
        regex = r'http://perdu.com/(?P<id>\d+).*'
        output = u'%(id)s'
        self.assertEqual(rgxformat(string, regex, output),
                         u'42')


class NormalizerObjectTestCase(unittest.TestCase):

    def test_normalizer(self):
        normalizer = BaseNormalizer(lunormalize)
        self.assertEqual(normalizer.normalize(u'bépoèàÀêùï'), u'bepoeaaeui')

    def test_normalizer_record(self):
        normalizer = BaseNormalizer(lunormalize, attr_index=1)
        record = ('a1', u'bépoèàÀêùï')
        self.assertEqual(normalizer.normalize(record), ['a1', u'bepoeaaeui'])

    def test_normalizer_dataset(self):
        normalizer = BaseNormalizer(lunormalize, attr_index=1)
        dataset = [('a1', u'bépoèàÀêùï'), ('a2', u'tàtà')]
        results = normalizer.normalize_dataset(dataset)
        self.assertEqual([['a1', u'bepoeaaeui'], ['a2', u'tata']], results)
        self.assertNotEqual(results, dataset)

    def test_normalizer_dataset_inplace(self):
        normalizer = BaseNormalizer(lunormalize, attr_index=1)
        dataset = [('a1', u'bépoèàÀêùï'), ('a2', u'tàtà')]
        normalizer.normalize_dataset(dataset, inplace=True)
        self.assertEqual([['a1', u'bepoeaaeui'], ['a2', u'tata']], dataset)

    def test_unormalize(self):
        normalizer = UnicodeNormalizer()
        self.assertEqual(normalizer.normalize(u'bépoèàÀêùï'), u'bepoeaaeui')

    def test_unormalize_record(self):
        normalizer = UnicodeNormalizer(attr_index=1)
        record = ('a1', u'bépoèàÀêùï')
        self.assertEqual(['a1', u'bepoeaaeui'], normalizer.normalize(record))

    def test_simplify(self):
        normalizer = SimplifyNormalizer(lemmas=FRENCH_LEMMAS)
        self.assertEqual(
            normalizer.normalize(u"J'aime les frites, les pommes et les scoubidous !"),
            u"aimer frites pomme scoubidou")

    def test_simplify_record(self):
        normalizer = SimplifyNormalizer(attr_index=1, lemmas=FRENCH_LEMMAS)
        self.assertEqual(['a1', u"aimer frites pomme scoubidou"],
                         normalizer.normalize(['a1', u"J'aime les frites, les pommes "
                                               "et les scoubidous !"]))

    def test_tokenize(self):
        normalizer = TokenizerNormalizer()
        self.assertEqual([u"J'", u'aime', u'les', u'frites', u'!', ],
                         normalizer.normalize(u"J'aime les frites !"))

    def test_tokenize_record(self):
        normalizer = TokenizerNormalizer(attr_index=1)
        self.assertEqual(['a1', [u"J'", u'aime', u'les', u'frites', u'!', ]],
                         normalizer.normalize(['a1', u"J'aime les frites !"]))

    def test_lemmatizer(self):
        normalizer = LemmatizerNormalizer(FRENCH_LEMMAS)
        self.assertEqual(normalizer.normalize(u'sacré rubert'), u'sacré rubert')
        self.assertEqual(normalizer.normalize(u"J'aime les frites !"), u'je aimer le frite')
        self.assertEqual(normalizer.normalize(u", J'aime les frites"), u'je aimer le frite')

    def test_lemmatizer_record(self):
        normalizer = LemmatizerNormalizer(FRENCH_LEMMAS, attr_index=1)
        self.assertEqual(['a1', u'sacré rubert'],
                         normalizer.normalize(['a1', u'sacré rubert']))
        self.assertEqual(['a1', u'je aimer le frite'],
                         normalizer.normalize(['a1', u"J'aime les frites !"]))
        self.assertEqual(['a1', u'je aimer le frite'],
                         normalizer.normalize(['a1', u", J'aime les frites"]))

    def test_round(self):
        normalizer = RoundNormalizer()
        self.assertEqual(normalizer.normalize(3.14159), '3')
        normalizer = RoundNormalizer(ndigits=2)
        self.assertEqual(normalizer.normalize(3.14159), '3.14')
        normalizer = RoundNormalizer(ndigits=3)
        self.assertEqual(normalizer.normalize(3.14159), '3.142')

    def test_round_record(self):
        normalizer = RoundNormalizer(attr_index=1)
        self.assertEqual(['a1', '3'], normalizer.normalize(['a1', 3.14159]))
        normalizer = RoundNormalizer(attr_index=1, ndigits=2)
        self.assertEqual(['a1', '3.14'], normalizer.normalize(['a1', 3.14159]))
        normalizer = RoundNormalizer(attr_index=1, ndigits=3)
        self.assertEqual(['a1', '3.142'], normalizer.normalize(['a1', 3.14159]))

    def test_regexp(self):
        normalizer = RegexpNormalizer(r'http://perdu.com/(?P<id>\d+).*', u'%(id)s')
        self.assertEqual(normalizer.normalize(u'http://perdu.com/42/supertop/cool'), u'42')

    def test_regexp_record(self):
        normalizer = RegexpNormalizer(r'http://perdu.com/(?P<id>\d+).*', u'%(id)s', attr_index=1)
        self.assertEqual(['a1', u'42'],
                         normalizer.normalize(['a1', u'http://perdu.com/42/supertop/cool']))

    def test_join(self):
        normalizer = JoinNormalizer((1, 2))
        self.assertEqual(normalizer.normalize((1, 'ab', 'cd', 'e', 5)), [1, 'e', 5, 'ab, cd'])


class NormalizerPipelineTestCase(unittest.TestCase):

    def test_normalizer(self):
        regexp = r'(?P<id>\d+);{["]?(?P<firstname>.+[^"])["]?};{(?P<surname>.*)};{};{};(?P<date>.*)'
        output = u'%(id)s\t%(firstname)s\t%(surname)s\t%(date)s'
        n1 = RegexpNormalizer(regexp, u'%(id)s\t%(firstname)s\t%(surname)s\t%(date)s')
        n2 = BaseNormalizer(callback=lambda x: x.split('\t'))
        n3 = UnicodeNormalizer(attr_index=(1, 2, 3))
        pipeline = NormalizerPipeline((n1, n2, n3))
        r1 = u'1111;{"Toto tàtà"};{Titi};{};{};'
        self.assertEqual(['1111', 'toto tata', 'titi', u''], pipeline.normalize(r1))


if __name__ == '__main__':
    unittest.main()
