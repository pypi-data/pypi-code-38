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

from nazca.utils.tokenizer import (RichStringTokenizer, Token,
                                   Sentence, NLTK_AVAILABLE)


@unittest.skipUnless(NLTK_AVAILABLE, 'nltk is not available')
class TokenizerTest(unittest.TestCase):
    """ Test of tokenizer """

    def test_find_sentences(self):
        text = 'Hello everyone, this is   me speaking. And me.'
        sentences = RichStringTokenizer.find_sentences(text)
        self.assertEqual(sentences[0], Sentence(indice=0, start=0, end=38))
        self.assertEqual(sentences[1], Sentence(indice=1, start=39, end=46))

    def test_richstringtokenizer(self):
        text = 'Hello everyone, this is   me speaking. And me.'
        tokenizer = RichStringTokenizer(text,
                                        token_min_size=1,
                                        token_max_size=3)
        tokens = list(tokenizer)
        self.assertEqual(len(tokens), 18)
        t1 = Token(
            word='Hello everyone this',
            start=0,
            end=20,
            sentence=Sentence(
                indice=0,
                start=0,
                end=38))
        self.assertEqual(tokens[0], t1)
        t2 = Token(word='And', start=39, end=42, sentence=Sentence(indice=1, start=39, end=46))
        self.assertEqual(tokens[16], t2)

    def test_richstringtokenizer_loadtext(self):
        text = 'Hello everyone, this is   me speaking. And me.'
        tokenizer = RichStringTokenizer(text,
                                        token_min_size=1,
                                        token_max_size=3)
        tokens = list(tokenizer)
        self.assertEqual(len(tokens), 18)
        tokenizer.load_text('Hello everyone')
        tokens = list(tokenizer)
        self.assertEqual(len(tokens), 3)

    def test_richstringtokenizer_minsize(self):
        text = 'Hello everyone, this is   me speaking. And me.'
        tokenizer = RichStringTokenizer(text,
                                        token_min_size=2,
                                        token_max_size=3)
        tokens = list(tokenizer)
        self.assertEqual(len(tokens), 10)
        t1 = Token(
            word='me speaking',
            start=26,
            end=37,
            sentence=Sentence(
                indice=0,
                start=0,
                end=38))
        self.assertEqual(tokens[8], t1)

    def test_richstringtokenizer_maxsize(self):
        text = 'Hello everyone, this is   me speaking. And me.'
        tokenizer = RichStringTokenizer(text,
                                        token_min_size=1,
                                        token_max_size=4)
        tokens = list(tokenizer)
        self.assertEqual(len(tokens), 21)
        t1 = Token(word='And me', start=39, end=45, sentence=Sentence(indice=1, start=39, end=46))
        self.assertEqual(tokens[18], t1)

    def test_richstringtokenizer_sentences(self):
        text = 'Hello everyone, this is   me speaking. And me ! Why not me ? Blup'
        tokenizer = RichStringTokenizer(text,
                                        token_min_size=1,
                                        token_max_size=4)
        sentences = tokenizer.find_sentences(text)
        self.assertEqual(len(sentences), 4)
        self.assertEqual(text[sentences[0].start:sentences[0].end],
                         'Hello everyone, this is   me speaking.')
        self.assertEqual(text[sentences[1].start:sentences[1].end],
                         'And me !')
        self.assertEqual(text[sentences[2].start:sentences[2].end],
                         'Why not me ?')
        self.assertEqual(text[sentences[3].start:sentences[3].end],
                         'Blup')


if __name__ == '__main__':
    unittest.main()
