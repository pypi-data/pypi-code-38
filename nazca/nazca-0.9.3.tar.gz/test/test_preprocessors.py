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

from nazca.utils import tokenizer
from nazca.ner import preprocessors


class PreprocessorTest(unittest.TestCase):
    """ Test of preprocessors """

    def test_lowercasefilter(self):
        preprocessor = preprocessors.NerLowerCaseFilterPreprocessor()
        token = tokenizer.Token('toto', 0, 4, None)
        self.assertEqual(preprocessor(token), None)
        token = tokenizer.Token('toto Tata', 0, 4, None)
        self.assertEqual(preprocessor(token), token)
        token = tokenizer.Token('toto tata', 0, 4, None)
        self.assertEqual(preprocessor(token), None)

    def test_wordsizefilter(self):
        preprocessor = preprocessors.NerWordSizeFilterPreprocessor()
        token = tokenizer.Token('toto', 0, 4, None)
        self.assertEqual(preprocessor(token), token)
        preprocessor = preprocessors.NerWordSizeFilterPreprocessor(min_size=3)
        token = tokenizer.Token('toto', 0, 4, None)
        self.assertEqual(preprocessor(token), token)
        token = tokenizer.Token('to', 0, 4, None)
        self.assertEqual(preprocessor(token), None)
        preprocessor = preprocessors.NerWordSizeFilterPreprocessor(max_size=3)
        token = tokenizer.Token('toto', 0, 4, None)
        self.assertEqual(preprocessor(token), None)
        token = tokenizer.Token('to', 0, 4, None)
        self.assertEqual(preprocessor(token), token)

    def test_lowerfirstword(self):
        preprocessor = preprocessors.NerLowerFirstWordPreprocessor()
        sentence = tokenizer.Sentence(0, 0, 20)
        # Start of the sentence
        token1 = tokenizer.Token('Toto tata', 0, 4, sentence)
        token2 = tokenizer.Token('Toto tata', 0, 4, sentence)
        self.assertEqual(preprocessor(token1), token2)
        token1 = tokenizer.Token('Us tata', 0, 4, sentence)
        token2 = tokenizer.Token('us tata', 0, 4, sentence)
        self.assertEqual(preprocessor(token1), token2)
        # Not start of the sentence
        token1 = tokenizer.Token('Toto tata', 12, 16, sentence)
        token2 = tokenizer.Token('Toto tata', 12, 16, sentence)
        self.assertEqual(preprocessor(token1), token2)
        token1 = tokenizer.Token('Us tata', 12, 16, sentence)
        token2 = tokenizer.Token('Us tata', 12, 16, sentence)
        self.assertEqual(preprocessor(token1), token2)

    def test_stopwordsfilter(self):
        preprocessor = preprocessors.NerStopwordsFilterPreprocessor()
        token = tokenizer.Token('Toto', 0, 4, None)
        self.assertEqual(preprocessor(token), token)
        token = tokenizer.Token('Us', 0, 4, None)
        self.assertEqual(preprocessor(token), None)
        token = tokenizer.Token('Us there', 0, 4, None)
        self.assertEqual(preprocessor(token), token)
        # Split words
        preprocessor = preprocessors.NerStopwordsFilterPreprocessor(split_words=True)
        token = tokenizer.Token('Us there', 0, 4, None)
        self.assertEqual(preprocessor(token), None)
        token = tokenizer.Token('Us there toto', 0, 4, None)
        self.assertEqual(preprocessor(token), token)

    def test_hashtag(self):
        preprocessor = preprocessors.NerHashTagPreprocessor()
        token = tokenizer.Token('Toto', 0, 4, None)
        self.assertEqual(preprocessor(token), token)
        token1 = tokenizer.Token('@BarackObama', 0, 4, None)
        token2 = tokenizer.Token('BarackObama', 0, 4, None)
        self.assertEqual(preprocessor(token1), token2)
        token1 = tokenizer.Token('@Barack_Obama', 0, 4, None)
        token2 = tokenizer.Token('Barack Obama', 0, 4, None)
        self.assertEqual(preprocessor(token1), token2)


if __name__ == '__main__':
    unittest.main()
