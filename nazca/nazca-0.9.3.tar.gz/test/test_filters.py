# -*- coding:utf-8 -*-
#
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from nazca.ner import NerProcess
from nazca.ner.filters import (NerOccurenceFilter,
                               NerReplacementRulesFilter,
                               NerDisambiguationWordParts)
from nazca.ner.sources import NerSourceLexicon
from nazca.utils.tokenizer import Token, Sentence, NLTK_AVAILABLE


@unittest.skipUnless(NLTK_AVAILABLE, 'nltk is not available')
class FilterTest(unittest.TestCase):
    """ Test of filters """

    def test_occurence_filter_min_occ(self):
        """ Test occurence filter """
        text = 'Hello everyone, this is   me speaking. And me.'
        source1 = NerSourceLexicon({'everyone': 'http://example.com/everyone',
                                    'me': 'http://example.com/me'})
        source2 = NerSourceLexicon({'me': 'http://example2.com/me'})
        _filter = NerOccurenceFilter(min_occ=2)
        ner = NerProcess((source1, source2), filters=(_filter,))
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/me', None,
                           Token(word='me', start=26, end=28,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example2.com/me', None,
                           Token(word='me', start=26, end=28,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example.com/me', None,
                           Token(word='me', start=43, end=45,
                                 sentence=Sentence(indice=1, start=39, end=46))),
                          ('http://example2.com/me', None,
                           Token(word='me', start=43, end=45,
                                 sentence=Sentence(indice=1, start=39, end=46)))])

    def test_occurence_filter_max_occ(self):
        """ Test occurence filter """
        text = 'Hello everyone, this is   me speaking. And me.'
        source1 = NerSourceLexicon({'everyone': 'http://example.com/everyone',
                                    'me': 'http://example.com/me'})
        source2 = NerSourceLexicon({'me': 'http://example2.com/me'})
        _filter = NerOccurenceFilter(max_occ=1)
        ner = NerProcess((source1, source2), filters=(_filter,))
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/everyone', None,
                           Token(word='everyone', start=6, end=14,
                                 sentence=Sentence(indice=0, start=0, end=38))), ])

    def test_disambiguation_word_length(self):
        """ Test occurence filter """
        text = 'Hello toto tutu. And toto.'
        source = NerSourceLexicon({'toto tutu': 'http://example.com/toto_tutu',
                                   'toto': 'http://example.com/toto'})
        _filter = NerDisambiguationWordParts()
        ner = NerProcess((source,), filters=(_filter,))
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/toto_tutu', None,
                           Token(word='toto tutu', start=6, end=15,
                                 sentence=Sentence(indice=0, start=0, end=16))),
                          ('http://example.com/toto_tutu', None,
                           Token(word='toto', start=21, end=25,
                                 sentence=Sentence(indice=1, start=17, end=26)))])

    def test_disambiguation_word_case(self):
        """ Test occurence filter """
        text = 'Hello Toto Tutu. And Toto.'
        source = NerSourceLexicon({'Toto Tutu': 'http://example.com/toto_tutu',
                                   'Toto': 'http://example.com/toto'})
        _filter = NerDisambiguationWordParts()
        ner = NerProcess((source,), filters=(_filter,))
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/toto_tutu', None,
                           Token(word='Toto Tutu', start=6, end=15,
                                 sentence=Sentence(indice=0, start=0, end=16))),
                          ('http://example.com/toto_tutu', None,
                           Token(word='Toto', start=21, end=25,
                                 sentence=Sentence(indice=1, start=17, end=26)))])

    def test_rules_filter(self):
        """ Test rules filter """
        text = 'Hello toto tutu. And toto.'
        source = NerSourceLexicon({'toto tutu': 'http://example.com/toto_tutu',
                                   'toto': 'http://example.com/toto'})
        rules = {'http://example.com/toto': 'http://example.com/tata'}
        _filter = NerReplacementRulesFilter(rules)
        ner = NerProcess((source,), filters=(_filter,))
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/toto_tutu', None,
                           Token(word='toto tutu', start=6, end=15,
                                 sentence=Sentence(indice=0, start=0, end=16))),
                          ('http://example.com/tata', None,
                           Token(word='toto', start=21, end=25,
                                 sentence=Sentence(indice=1, start=17, end=26)))])


if __name__ == '__main__':
    unittest.main()
