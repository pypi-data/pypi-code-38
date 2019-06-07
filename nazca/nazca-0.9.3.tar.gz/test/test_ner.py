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

from nazca.ner.sources import (NerSourceLexicon,
                               NerSourceSparql,
                               NerSourceRql)
from nazca.ner import NerProcess
from nazca.utils.tokenizer import Token, Sentence, NLTK_AVAILABLE
from nazca.ner.preprocessors import NerStopwordsFilterPreprocessor
from nazca.utils.dataio import SPARQL_ENABLED


class NerTest(unittest.TestCase):
    """ Test of Ner """

    def test_lexicon_source(self):
        """ Test lexicon source """
        lexicon = {'everyone': 'http://example.com/everyone',
                   'me': 'http://example.com/me'}
        source = NerSourceLexicon(lexicon)
        self.assertEqual(source.query_word('me'), ['http://example.com/me', ])
        self.assertEqual(source.query_word('everyone'), ['http://example.com/everyone', ])
        self.assertEqual(source.query_word('me everyone'), [])
        self.assertEqual(source.query_word('toto'), [])
        # Token
        token = Token('me', 0, 2, None)
        self.assertEqual(source.recognize_token(token), ['http://example.com/me', ])
        token = Token('ma', 0, 2, None)
        self.assertEqual(source.recognize_token(token), [])

    def test_rql_source(self):
        """ Test rql source """
        source = NerSourceRql('http://www.cubicweb.org',
                              'Any U LIMIT 1 WHERE X cwuri U, X name "%(word)s"')
        self.assertEqual(source.query_word('apycot'), [u'http://www.cubicweb.org/1310453', ])

    @unittest.skipUnless(SPARQL_ENABLED, 'python-sparqlwrapper is not installed')
    def test_sparql_source(self):
        """ Test sparql source """
        source = NerSourceSparql(u'http://dbpedia.org/sparql',
                                 u'''SELECT DISTINCT ?uri
                                 WHERE {
                                 ?uri rdf:type <http://dbpedia.org/ontology/ProgrammingLanguage> ;
                                      dbpedia-owl:designer <http://dbpedia.org/resource/Guido_van_Rossum> ;
                                      rdfs:label ?label.
                                 FILTER(regex(?label, "^%(word)s"))
                                 }''')
        self.assertEqual(source.query_word('Python'),
                         ['http://dbpedia.org/resource/Python_(programming_language)',
                          'http://dbpedia.org/resource/Python_for_S60'])

    @unittest.skipUnless(NLTK_AVAILABLE, 'nltk is not available')
    def test_ner_process(self):
        """ Test ner process """
        text = 'Hello everyone, this is   me speaking. And me.'
        source = NerSourceLexicon({'everyone': 'http://example.com/everyone',
                                   'me': 'http://example.com/me'})
        ner = NerProcess((source,))
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/everyone', None,
                           Token(word='everyone', start=6, end=14,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example.com/me', None,
                           Token(word='me', start=26, end=28,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example.com/me', None,
                           Token(word='me', start=43, end=45,
                                 sentence=Sentence(indice=1, start=39, end=46)))])

    @unittest.skipUnless(NLTK_AVAILABLE, 'nltk is not available')
    def test_ner_process_multisources(self):
        """ Test ner process """
        text = 'Hello everyone, this is   me speaking. And me.'
        source1 = NerSourceLexicon({'everyone': 'http://example.com/everyone',
                                    'me': 'http://example.com/me'})
        source2 = NerSourceLexicon({'me': 'http://example2.com/me'})
        # Two sources, not unique
        ner = NerProcess((source1, source2))
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/everyone', None,
                           Token(word='everyone', start=6, end=14,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example.com/me', None,
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
        # Two sources, unique
        ner = NerProcess((source1, source2), unique=True)
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/everyone', None,
                           Token(word='everyone', start=6, end=14,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example.com/me', None,
                           Token(word='me', start=26, end=28,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example.com/me', None,
                           Token(word='me', start=43, end=45,
                                 sentence=Sentence(indice=1, start=39, end=46)))])
        # Two sources inversed, unique
        ner = NerProcess((source2, source1), unique=True)
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/everyone', None,
                           Token(word='everyone', start=6, end=14,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example2.com/me', None,
                           Token(word='me', start=26, end=28,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example2.com/me', None,
                           Token(word='me', start=43, end=45,
                                 sentence=Sentence(indice=1, start=39, end=46)))])

    @unittest.skipUnless(NLTK_AVAILABLE, 'nltk is not available')
    def test_ner_process_add_sources(self):
        """ Test ner process """
        text = 'Hello everyone, this is   me speaking. And me.'
        source1 = NerSourceLexicon({'everyone': 'http://example.com/everyone',
                                    'me': 'http://example.com/me'})
        source2 = NerSourceLexicon({'me': 'http://example2.com/me'})
        ner = NerProcess((source1,))
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/everyone', None,
                           Token(word='everyone', start=6, end=14,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example.com/me', None,
                           Token(word='me', start=26, end=28,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example.com/me', None,
                           Token(word='me', start=43, end=45,
                                 sentence=Sentence(indice=1, start=39, end=46))), ])
        # Two sources, not unique
        ner.add_ner_source(source2)
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/everyone', None,
                           Token(word='everyone', start=6, end=14,
                                 sentence=Sentence(indice=0, start=0, end=38))),
                          ('http://example.com/me', None,
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

    @unittest.skipUnless(NLTK_AVAILABLE, 'nltk is not available')
    def test_ner_process_preprocess(self):
        """ Test ner process """
        text = 'Hello Toto, this is   me speaking. And me.'
        source = NerSourceLexicon({'Toto': 'http://example.com/toto',
                                   'me': 'http://example.com/me'})
        preprocessor = NerStopwordsFilterPreprocessor()
        ner = NerProcess((source,),
                         preprocessors=(preprocessor,))
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities, [('http://example.com/toto', None,
                                           Token(word='Toto', start=6, end=10,
                                                 sentence=Sentence(indice=0, start=0, end=34)))])

    @unittest.skipUnless(NLTK_AVAILABLE, 'nltk is not available')
    def test_ner_process_add_preprocess(self):
        """ Test ner process """
        text = 'Hello Toto, this is   me speaking. And me.'
        source = NerSourceLexicon({'Toto': 'http://example.com/toto',
                                   'me': 'http://example.com/me'})
        preprocessor = NerStopwordsFilterPreprocessor()
        ner = NerProcess((source,),)
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/toto', None,
                           Token(word='Toto', start=6, end=10,
                                 sentence=Sentence(indice=0, start=0, end=34))),
                          ('http://example.com/me', None,
                           Token(word='me', start=22, end=24,
                                 sentence=Sentence(indice=0, start=0, end=34))),
                          ('http://example.com/me', None,
                           Token(word='me', start=39, end=41,
                                 sentence=Sentence(indice=1, start=35, end=42)))])
        ner.add_preprocessors(preprocessor)
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities, [('http://example.com/toto', None,
                                           Token(word='Toto', start=6, end=10,
                                                 sentence=Sentence(indice=0, start=0, end=34)))])

    @unittest.skipUnless(NLTK_AVAILABLE, 'nltk is not available')
    def test_ner_process_chained_word(self):
        """ Test ner process """
        text = 'Hello everyone me, this is   me speaking. And me.'
        source = NerSourceLexicon({'everyone': 'http://example.com/everyone',
                                   'everyone me': 'http://example.com/everyone_me',
                                   'me': 'http://example.com/me'})
        ner = NerProcess((source,))
        named_entities = ner.process_text(text)
        self.assertEqual(named_entities,
                         [('http://example.com/everyone_me', None,
                           Token(word='everyone me', start=6, end=17,
                                 sentence=Sentence(indice=0, start=0, end=41))),
                          ('http://example.com/me', None,
                           Token(word='me', start=29, end=31,
                                 sentence=Sentence(indice=0, start=0, end=41))),
                          ('http://example.com/me', None,
                           Token(word='me', start=46, end=48,
                                 sentence=Sentence(indice=1, start=42, end=49)))])


if __name__ == '__main__':
    unittest.main()
