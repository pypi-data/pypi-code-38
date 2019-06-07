# -*- coding:utf-8 -*-
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
from __future__ import print_function

from six import itervalues
from six.moves import cPickle, xrange

from random import randint
from collections import defaultdict

import numpy as np
from scipy.optimize import bisect


###############################################################################
# UTILITY FUNCTIONS ###########################################################
###############################################################################
def randomhashfunction(zr):
    """ Return a random hash function, mapping x in Z to ZR
        h:x -> ax + b mod R

    """
    bound = max(zr - 1, 1)
    a = randint(1, bound)
    b = randint(1, bound)

    def hashfunc(x):
        return ((a * x + b) % zr)

    return hashfunc


def count_vectorizer_func(sentences, min_n, max_n):
    """ Perform a tokenization using scikit learn
    """
    import sklearn
    import sklearn.feature_extraction.text as sklt
    skversion = tuple(int(x) for x in sklearn.__version__.split('.')[:2])
    if skversion < (0, 11):
        word_ngram = sklt.WordNGramAnalyzer(min_n=min_n, max_n=max)
        count_vec = sklt.CountVectorizer(analyzer=word_ngram)
    elif skversion < (0, 14):
        count_vec = sklt.CountVectorizer(min_n=min_n, max_n=max_n)
    else:
        count_vec = sklt.CountVectorizer(ngram_range=(min_n, max_n))
    # Transform and convert to lil to get rows
    data = count_vec.fit_transform(sentences).tolil()
    return [list(l) for l in data.rows], data.shape


###############################################################################
# MINHASHING ##################################################################
###############################################################################
class Minlsh(object):
    """ Operate minhashing + locally-sensitive-hashing to find similar sentences
    """

    def __init__(self, tokenizer_func=None, verbose=False):
        """ Initialize a minhashing/lsh object

        Parameters:
        ==========

           * tokenizer_func is a function that take the sentences
             as argument and return the rows of the sparse matrix
             of tokens, and its shape.

           * verbose is a boolean that trigger the display of
             some informations
        """
        self._trained = False
        self.sigmatrix = None
        if tokenizer_func:
            # Use given tokenizer_func
            self._buildmatrixdocument = lambda x, y: tokenizer_func(x)
        self._verbose = verbose

    def train(self, sentences, k=2, siglen=200):
        """ Train the minlsh on the given sentences.

            - `k` is the length of the k-wordgrams used
              (the lower k is, the faster is the training)
            - `siglen` the length of the sentences signature

        """
        rows, shape = self._buildmatrixdocument(sentences, k)
        if self._verbose:
            print("Training is done. Wait while signaturing")
        self._computesignaturematrix(rows, shape, siglen)
        self._trained = True

    def _iter_wordgrams(self, sentence, k):
        """ Generator of k-wordgrams on the given sentence
        """
        words = sentence.split(' ')
        for r in xrange(len(words)):
            for width in range(1, k + 1):
                if r + width <= len(words):
                    yield ' '.join(words[r:r + width])

    def _buildmatrixdocument(self, sentences, k):
        """ Return a sparse matrix where :

            - Each sentence is a column
            - Each row is a element of the universal set

            Each value (r, c) is set to 1 if the element at row r is in the
            sentence c, 0 otherwise

        """
        # Use default mode
        rows, universe, sizeofuniverse = [], {}, 0
        for nb, sent in enumerate(sentences):
            row = []
            for w in self._iter_wordgrams(sent, k):
                row.append(universe.setdefault(w, sizeofuniverse))
                if row[-1] == sizeofuniverse:
                    sizeofuniverse += 1
            rows.append(row)
            if self._verbose and nb % 50000 == 0:
                print(nb)

        return rows, (len(rows), sizeofuniverse)

    def _computesignaturematrix(self, rows, shape, siglen):
        """ Return a matrix where each column is the signature the document
            The signature is composed of `siglen` numbers

            The more the documents have rows in commun, the closer they are.
        """

        nrows, ncols = shape
        sig = np.empty((siglen, nrows))
        # Generate the random hash functions
        hashfunc = [randomhashfunction(ncols) for _ in xrange(siglen)]
        # Compute hashing values just for once.
        # Avoid multiple recomputations for the same column.
        hashvalues = np.array([[hashfunc[i](r) for r in xrange(ncols)]
                               for i in xrange(siglen)])

        docind = 0
        while rows:
            doc = rows.pop(0)
            # Concatenate the needed rows.
            tmp = np.dstack([hashvalues[:, r] for r in doc])
            # Take the mininum of hashes
            sig[:, docind] = np.min(tmp[0], 1)
            docind += 1
            if self._verbose and docind % 50000 == 0:
                print((docind * 100) / nrows)
        self.sigmatrix = sig

    def save(self, savefile):
        """ Save the training into `savefile` for a future use """

        if not self._trained:
            print("Not trained, nothing to save")
            return

        with open(savefile, 'wb') as fobj:
            pickler = cPickle.Pickler(fobj)
            pickler.dump(self.sigmatrix)

    def load(self, savefile):
        """ Load a trained minhashing """

        with open(savefile, 'rb') as fobj:
            pickler = cPickle.Unpickler(fobj)
            self.sigmatrix = pickler.load()

        if self.sigmatrix is not None:
            self._trained = True
        else:
            self._trained = False

    def computebandsize(self, threshold, nbrows):
        """ Compute the bandsize according to the threshold given """

        # t ~ (1/b)^(1/r), where t is the threshold, b the number of
        # bands, and r the number of rows per band. And nbrows (the length
        # of the matrix is nbrows = b*r, so t ~ (r/L)^(1/r). So, let's
        # find the root of f(x) = (x/L)^(1/r) - t.
        def f(x):
            y = pow(x / nbrows, 1. / x) - threshold
            return y

        # Solve f(x) = 0, with x having values in [1, nbrows]
        return int(bisect(f, 1, nbrows))

    def predict(self, threshold, minclustersize=2):
        """ Return a set of tuples of *possible* similar sentences
        """
        if not self._trained:
            print("Train it before")
            return

        if not (0 < threshold <= 1):
            print("Threshold must be in ]0 ; 1]")
            return

        sig = self.sigmatrix
        # Treshold is a percent of similarity
        # It should be inverted here (0 is closed, 1 is far)
        threshold = 1 - threshold
        bandsize = self.computebandsize(threshold, self.sigmatrix.shape[0])

        buckets = defaultdict(set)
        similars = set()
        for r in xrange(0, sig.shape[0], bandsize):
            buckets.clear()
            for i in xrange(sig.shape[1]):
                buckets[tuple(sig[r:r + bandsize, i])].add(i)
            similars.update(set(tuple(v) for v in itervalues(buckets)
                                if len(v) >= minclustersize))
        return similars
