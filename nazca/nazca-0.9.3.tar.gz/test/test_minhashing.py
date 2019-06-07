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
from functools import partial
from os import path
import random
random.seed(6)  # Make sure tests are repeatable

from nazca.utils.normalize import simplify
from nazca.utils.minhashing import Minlsh, count_vectorizer_func
from nazca.data import FRENCH_LEMMAS

TESTDIR = path.dirname(__file__)


class MinLSHTest(unittest.TestCase):

    def test_iter_wordgrams(self):
        sentence = 'nom de la rose'
        minlsh = Minlsh()
        results = list(minlsh._iter_wordgrams(sentence, 2))
        truth = ['nom de', 'nom', 'de la', 'de', 'la rose', 'la', 'rose']
        self.assertEqual(len(results), len(truth))
        self.assertEqual(set(results), set(truth))

    def test_iter_wordgrams_sklearn(self):
        sentences = ('nom de la rose', 'nom de la')
        tokenizer_func = partial(count_vectorizer_func, min_n=1, max_n=2)
        minlsh = Minlsh(tokenizer_func=tokenizer_func)
        rows, shape = list(minlsh._buildmatrixdocument(sentences, 2))
        self.assertEqual(shape, (2, 7))
        self.assertEqual(rows[0], [0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(rows[1], [0, 1, 2, 4, 5])

    def test_all(self):
        sentences = [u"Un nuage flotta dans le grand ciel bleu.",
                     u"Des grands nuages noirs flottent dans le ciel.",
                     u"Je n'aime pas ce genre de bandes dessinées tristes.",
                     u"J'aime les bandes dessinées de genre comiques.",
                     u"Pour quelle occasion vous êtes-vous apprêtée ?",
                     u"Je les vis ensemble à plusieurs occasions.",
                     u"Je les ai vus ensemble à plusieurs occasions.",
                     ]
        minlsh = Minlsh()
        # XXX Should works independantly of the seed. Unstability due to the bands number ?
        minlsh.train((simplify(s, FRENCH_LEMMAS, remove_stopwords=True) for s in sentences), 1, 200)
        self.assertEqual(set([(0, 1), (2, 3), (5, 6)]), minlsh.predict(0.4))


if __name__ == '__main__':
    unittest.main()
