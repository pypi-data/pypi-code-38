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


""" Blocking techniques.

This module implements a set of blocking techniques used to split
datasets in smaller subsets that will be aligned in more details.

Additional information:

   P. Christen, Data Matching, Data-Centric Systems and Applications,


"""
from functools import partial

from six import iteritems, itervalues
from six.moves import xrange

from scipy.spatial import KDTree

from nazca.utils.minhashing import Minlsh
from nazca.utils.distances import soundexcode


###############################################################################
# GENERAL BLOCKING ############################################################
###############################################################################
class BaseBlocking(object):
    """ An abstract general blocking object that exposes
    the API that should be common to all blockings object
    """

    def __init__(self, ref_attr_index, target_attr_index):
        """ Build the blocking object

        Parameters
        ----------

        ref_attr_index: index of the attribute of interest in a record
                        for the reference dataset
                        (i.e. attribute to be used for key computation)

        target_attr_index: index of the attribute of interest in a record
                           for the target dataset
                           (i.e. attribute to be used for key computation)
        """
        self.ref_attr_index = ref_attr_index
        self.target_attr_index = target_attr_index
        self.refids = None
        self.targetids = None
        self.is_fitted = False

    def _fit(self, refset, targetset):
        raise NotImplementedError

    def _iter_blocks(self):
        """ Internal iteration function over blocks
        """
        raise NotImplementedError

    def _cleanup(self):
        """ Internal cleanup blocking for further use (e.g. in pipeline)
        """
        raise NotImplementedError

    def fit(self, refset, targetset):
        """ Fit the blocking technique on the reference and target datasets

        Parameters
        ----------
        refset: a dataset (list of records)

        targetset: a dataset (list of records)
        """
        self._fit(refset, targetset)
        # Keep ids for blocks building
        self.refids = [(i, r[0]) for i, r in enumerate(refset)]
        self.targetids = [(i, r[0]) for i, r in enumerate(targetset)]
        self.is_fitted = True

    def iter_blocks(self):
        """ Iterator over the different possible blocks.

        Returns
        -------

        (block1, block2): The blocks are always (reference_block, target_block)
                          and contains the pair (index, id) of the record in the
                          corresponding dataset.
        """
        assert self.is_fitted
        return self._iter_blocks()

    def iter_indice_blocks(self):
        """ Iterator over the different possible blocks.

        Returns
        -------

        (block1, block2): The blocks are always (reference_block, target_block)
                          and contains the indexes of the record in the
                          corresponding dataset.
        """
        assert self.is_fitted
        for block1, block2 in self._iter_blocks():
            yield [r[0] for r in block1], [r[0] for r in block2]

    def iter_id_blocks(self):
        """ Iterator over the different possible blocks.

        Returns
        -------

        (block1, block2): The blocks are always (reference_block, target_block)
                          and contains the ids of the record in the
                          corresponding dataset.
        """
        assert self.is_fitted
        for block1, block2 in self._iter_blocks():
            yield [r[1] for r in block1], [r[1] for r in block2]

    def iter_pairs(self):
        """ Iterator over the different possible pairs.

        Returns
        -------

        (pair1, pari2): The pairs are always ((ind_reference, id_reference),
                                              (ind_target, id_target))
                        and are the ids of the record in the corresponding dataset.
        """
        assert self.is_fitted
        for block1, block2 in self.iter_blocks():
            for val1 in block1:
                for val2 in block2:
                    yield val1, val2

    def iter_indice_pairs(self):
        """ Iterator over the different possible pairs.

        Returns
        -------

        (pair1, pari2): The pairs are always (ind_reference, ind_target)
                        and are the ids of the record in the corresponding dataset.
        """
        assert self.is_fitted
        for block1, block2 in self.iter_indice_blocks():
            for val1 in block1:
                for val2 in block2:
                    yield val1, val2

    def iter_id_pairs(self):
        """ Iterator over the different possible pairs.

        Returns
        -------

        (pair1, pari2): The pairs are always (id_reference, id_target)
                        and are the ids of the record in the corresponding dataset.
        """
        assert self.is_fitted
        for block1, block2 in self.iter_id_blocks():
            for val1 in block1:
                for val2 in block2:
                    yield val1, val2

    def cleanup(self):
        """ Cleanup blocking for further use (e.g. in pipeline)
        """
        self.is_fitted = True
        self._cleanup()


###############################################################################
# KEY BLOCKING ################################################################
###############################################################################
class KeyBlocking(BaseBlocking):
    """ This blocking technique is based on a a blocking criteria
    (or blocking key), that will be used to divide the datasets.

    The main idea here is:

    1 - to create an index of f(x) for each x in the reference set.

    2 - to create an index of f(y) for each y in the target set.

    3 - to iterate on each distinct value of f(x) and to return
        the identifiers of the records of the both sets for this value.
    """

    def __init__(self, ref_attr_index, target_attr_index,
                 callback, ignore_none=False):
        super(KeyBlocking, self).__init__(ref_attr_index, target_attr_index)
        self.callback = callback
        self.ignore_none = ignore_none
        self.reference_index = {}
        self.target_index = {}

    def _fit(self, refset, targetset):
        """ Fit a dataset in an index using the callback
        """
        for ind, rec in enumerate(refset):
            key = self.callback(rec[self.ref_attr_index])
            if not key and self.ignore_none:
                continue
            self.reference_index.setdefault(key, []).append((ind, rec[0]))
        for ind, rec in enumerate(targetset):
            key = self.callback(rec[self.target_attr_index])
            if not key and self.ignore_none:
                continue
            self.target_index.setdefault(key, []).append((ind, rec[0]))

    def _iter_blocks(self):
        """ Iterator over the different possible blocks.

        Returns
        -------

        (block1, block2): The blocks are always (reference_block, target_block)
                          and containts the indexes of the record in the
                          corresponding dataset.
        """
        for key, block1 in iteritems(self.reference_index):
            block2 = self.target_index.get(key)
            if block1 and block2:
                yield (block1, block2)

    def _cleanup(self):
        """ Cleanup blocking for further use (e.g. in pipeline)
        """
        self.reference_index = {}
        self.target_index = {}


class SoundexBlocking(KeyBlocking):

    def __init__(self, ref_attr_index, target_attr_index, language='french',):
        super(SoundexBlocking, self).__init__(ref_attr_index, target_attr_index,
                                              partial(soundexcode, language=language))


###############################################################################
# BIGRAM BLOCKING #############################################################
###############################################################################
class NGramBlocking(BaseBlocking):
    """ This blocking technique is based on a a n-gram key.
    """

    def __init__(self, ref_attr_index, target_attr_index,
                 ngram_size=2, depth=2):
        super(NGramBlocking, self).__init__(ref_attr_index, target_attr_index)
        self.ngram_size = ngram_size
        self.depth = depth
        self.reference_index = {}
        self.target_index = {}

    def _fit_dataset(self, dataset, cur_index, attr_index):
        """ Fit a dataset
        """
        for ind, r in enumerate(dataset):
            cur_dict = cur_index
            text = r[attr_index]
            for i in range(self.depth):
                ngram = text[i * self.ngram_size:(i + 1) * self.ngram_size]
                if i < self.depth - 1:
                    cur_dict = cur_dict.setdefault(ngram, {})
            cur_dict.setdefault(ngram, []).append((ind, r[0]))

    def _fit(self, refset, targetset):
        """ Fit the two sets (reference set and target set)
        """
        self._fit_dataset(refset, self.reference_index, self.ref_attr_index)
        self._fit_dataset(targetset, self.target_index, self.target_attr_index)

    def _iter_dict(self, ref_cur_dict, target_cur_dict):
        """ Iterative function used to create blocks from dicts
        """
        for key, sub_dict in iteritems(ref_cur_dict):
            if key in target_cur_dict:
                if isinstance(sub_dict, dict):
                    # There is another dict layer
                    for block1, block2 in self._iter_dict(
                            sub_dict, target_cur_dict[key]):
                        yield block1, block2
                else:
                    # This is a list
                    yield sub_dict, target_cur_dict[key]

    def _iter_blocks(self):
        """ Iterator over the different possible blocks.

        Returns
        -------

        (block1, block2): The blocks are always (reference_block, target_block)
                          and containts the indexes of the record in the
                          corresponding dataset.
        """
        for block1, block2 in self._iter_dict(
                self.reference_index, self.target_index):
            if block1 and block2:
                yield block1, block2

    def _cleanup(self):
        """ Cleanup blocking for further use (e.g. in pipeline)
        """
        self.reference_index = {}
        self.target_index = {}


###############################################################################
# SORTKEY BLOCKING ############################################################
###############################################################################
class SortedNeighborhoodBlocking(BaseBlocking):
    """ This blocking technique is based on a a sorting blocking criteria
    (or blocking key), that will be used to divide the datasets.
    """

    def __init__(self, ref_attr_index, target_attr_index,
                 key_func=lambda x: x, window_width=20):
        super(
            SortedNeighborhoodBlocking,
            self).__init__(
            ref_attr_index,
            target_attr_index)
        self.key_func = key_func
        self.window_width = window_width
        self.sorted_dataset = None

    def _fit(self, refset, targetset):
        """ Fit a dataset in an index using the callback
        """
        self.sorted_dataset = [((ind, r[0]), r[self.ref_attr_index], 0)
                               for ind, r in enumerate(refset)]
        self.sorted_dataset.extend([((ind, r[0]), r[self.target_attr_index], 1)
                                    for ind, r in enumerate(targetset)])
        self.sorted_dataset.sort(key=lambda x: self.key_func(x[1]))

    def _iter_blocks(self):
        """ Iterator over the different possible blocks.
        """
        for ind, (rid, record, dset) in enumerate(self.sorted_dataset):
            # Only keep reference set record
            if dset == 1:
                continue
            block1 = [rid, ]
            minind = (ind - self.window_width)
            minind = minind if minind >= 0 else 0
            maxind = (ind + self.window_width + 1)
            block2 = [ri for ri, re, d in self.sorted_dataset[minind:maxind]
                      if d == 1]
            if block1 and block2:
                yield (block1, block2)

    def _cleanup(self):
        """ Cleanup blocking for further use (e.g. in pipeline)
        """
        self.sorted_dataset = None


###############################################################################
# MERGE BLOCKING ##############################################################
###############################################################################
class MergeBlocking(BaseBlocking):
    """ This blocking technique keep only one appearance of one given values,
    and removes all the other records having this value.
    The merge is based on a score function

    E.g.
      ('http://fr.wikipedia.org/wiki/Paris_%28Texas%29', 'Paris', 25898)
      ('http://fr.wikipedia.org/wiki/Paris', 'Paris', 12223100)

    could be (with a score function based on the population (third value):

      ('http://fr.wikipedia.org/wiki/Paris', 'Paris', 12223100)

    !!! WARNING !!! This is only done on ONE set (the one with a non null attr index)
    """

    def __init__(self, ref_attr_index, target_attr_index, score_func):
        super(MergeBlocking, self).__init__(ref_attr_index, target_attr_index)
        self.score_func = score_func
        self.merged_dataset = None
        self.other_dataset = None
        if ref_attr_index is None and target_attr_index is None:
            raise ValueError('At least one of ref_attr_index or target_attr_index '
                             'should not be None')

    def _fit(self, refset, targetset):
        """ Fit a dataset in an index using the callback
        """
        if self.ref_attr_index is not None:
            # Merge refset
            self.merged_dataset = self._merge_dataset(
                refset, self.ref_attr_index)
            self.other_dataset = [(ind, r[0])
                                  for ind, r in enumerate(targetset)]
        else:
            # Merge targetset
            self.merged_dataset = self._merge_dataset(
                targetset, self.target_attr_index)
            self.other_dataset = [(ind, r[0]) for ind, r in enumerate(refset)]

    def _merge_dataset(self, dataset, attr_index):
        """ Merge a dataset
        """
        merged_dataset_dict = {}
        for ind, record in enumerate(dataset):
            score = self.score_func(record)
            if record[attr_index] not in merged_dataset_dict:
                # Create new entry
                merged_dataset_dict[record[attr_index]] = (ind, record, score)
            elif (record[attr_index] in merged_dataset_dict
                  and merged_dataset_dict[record[attr_index]][2] < score):
                # Change current score
                merged_dataset_dict[record[attr_index]] = (ind, record, score)
        return [(ind, r[0])
                for ind, r, score in itervalues(merged_dataset_dict)]

    def _iter_blocks(self):
        """ Iterator over the different possible blocks.
        """
        if self.ref_attr_index is not None:
            yield self.merged_dataset, self.other_dataset
        else:
            # self.target_attr_index is not None
            yield self.other_dataset, self.merged_dataset

    def _cleanup(self):
        """ Cleanup blocking for further use (e.g. in pipeline)
        """
        self.merged_dataset = None
        self.other_dataset = None


###############################################################################
# CLUSTERING-BASED BLOCKINGS ##################################################
###############################################################################
class KmeansBlocking(BaseBlocking):
    """ A blocking technique based on Kmeans
    """

    def __init__(self, ref_attr_index, target_attr_index, n_clusters=None):
        super(KmeansBlocking, self).__init__(ref_attr_index, target_attr_index)
        self.n_clusters = n_clusters
        self.kmeans = None
        self.predicted = None
        from sklearn import cluster
        self.cluster_class = cluster.KMeans

    def _fit(self, refset, targetset):
        """ Fit the reference dataset.
        """
        # If an element is None (missing), use instead the identity element.
        # The identity element is defined as the 0-vector
        idelement = tuple(
            [0 for _ in xrange(len(refset[0][self.ref_attr_index]))])
        # We assume here that there are at least 2 elements in the refset
        n_clusters = self.n_clusters or (len(refset) / 10 or len(refset) / 2)
        try:
            kmeans = self.cluster_class(n_clusters=n_clusters)
        except TypeError:
            # Try older API version of sklearn
            kmeans = self.cluster_class(k=n_clusters)
        kmeans.fit([elt[self.ref_attr_index] or idelement for elt in refset])
        self.kmeans = kmeans
        # Predict on targetset
        self.predicted = self.kmeans.predict([elt[self.target_attr_index]
                                              or idelement for elt in targetset])

    def _iter_blocks(self):
        """ Iterator over the different possible blocks.

        Returns
        -------

        (block1, block2): The blocks are always (reference_block, target_block)
                          and containts the indexes of the record in the
                          corresponding dataset.
        """
        n_clusters = self.kmeans.n_clusters if hasattr(
            self.kmeans, 'n_clusters') else self.kmeans.k
        neighbours = [[[], []] for _ in xrange(n_clusters)]
        for ind, li in enumerate(self.predicted):
            neighbours[li][1].append(self.targetids[ind])
        for ind, li in enumerate(self.kmeans.labels_):
            neighbours[li][0].append(self.refids[ind])
        for block1, block2 in neighbours:
            if len(block1) and len(block2):
                yield block1, block2

    def _cleanup(self):
        """ Cleanup blocking for further use (e.g. in pipeline)
        """
        self.kmeans = None
        self.predicted = None


###############################################################################
# KDTREE BLOCKINGS ############################################################
###############################################################################
class KdTreeBlocking(BaseBlocking):
    """ A blocking technique based on KdTree
    """

    def __init__(self, ref_attr_index, target_attr_index, threshold=0.1):
        super(KdTreeBlocking, self).__init__(ref_attr_index, target_attr_index)
        self.threshold = threshold
        self.reftree = None
        self.targettree = None
        self.nb_elements = None

    def _fit(self, refset, targetset):
        """ Fit the blocking
        """
        firstelement = refset[0][self.ref_attr_index]
        self.nb_elements = len(refset)
        idsize = len(firstelement) if isinstance(
            firstelement, (tuple, list)) else 1
        idelement = (0,) * idsize
        # KDTree is expecting a two-dimensional array
        if idsize == 1:
            self.reftree = KDTree(
                [(elt[self.ref_attr_index],) or idelement for elt in refset])
            self.targettree = KDTree(
                [(elt[self.target_attr_index],) or idelement for elt in targetset])
        else:
            self.reftree = KDTree(
                [elt[self.ref_attr_index] or idelement for elt in refset])
            self.targettree = KDTree(
                [elt[self.target_attr_index] or idelement for elt in targetset])

    def _iter_blocks(self):
        """ Iterator over the different possible blocks.

        Returns
        -------

        (block1, block2): The blocks are always (reference_block, target_block)
                          and containts the indexes of the record in the
                          corresponding dataset.
        """
        extraneighbours = self.reftree.query_ball_tree(
            self.targettree, self.threshold)
        neighbours = []
        for ind in xrange(self.nb_elements):
            if not extraneighbours[ind]:
                continue
            _ref = [self.refids[ind], ]
            _target = [self.targetids[v] for v in extraneighbours[ind]]
            neighbours.append((_ref, _target))
        for block1, block2 in neighbours:
            if len(block1) and len(block2):
                yield block1, block2

    def _cleanup(self):
        """ Cleanup blocking for further use (e.g. in pipeline)
        """
        self.reftree = None
        self.targettree = None
        self.nb_elements = None


###############################################################################
# MINHASHING BLOCKINGS ########################################################
###############################################################################
class MinHashingBlocking(BaseBlocking):
    """ A blocking technique based on MinHashing
    """

    def __init__(self, ref_attr_index, target_attr_index,
                 threshold=0.1, kwordsgram=1, siglen=200):
        super(
            MinHashingBlocking,
            self).__init__(
            ref_attr_index,
            target_attr_index)
        self.threshold = threshold
        self.kwordsgram = kwordsgram
        self.siglen = siglen
        self.minhasher = Minlsh()
        self.nb_elements = None

    def _fit(self, refset, targetset):
        """ Find the blocking using minhashing
        """
        # If an element is None (missing), use instead the identity element.
        idelement = ''
        self.minhasher.train([elt[self.ref_attr_index] or idelement for elt in refset] +
                             [elt[self.target_attr_index]
                                 or idelement for elt in targetset],
                             self.kwordsgram, self.siglen)
        self.nb_elements = len(refset)

    def _iter_blocks(self):
        """ Iterator over the different possible blocks.

        Returns
        -------

        (block1, block2): The blocks are always (reference_block, target_block)
                          and containts the indexes of the record in the
                          corresponding dataset.
        """
        rawneighbours = self.minhasher.predict(self.threshold)
        neighbours = []
        for data in rawneighbours:
            neighbours.append([[], []])
            for i in data:
                if i >= self.nb_elements:
                    neighbours[-1][1].append(self.targetids[i -
                                                            self.nb_elements])
                else:
                    neighbours[-1][0].append(self.refids[i])
            if len(neighbours[-1][0]) == 0 or len(neighbours[-1][1]) == 0:
                neighbours.pop()
        for block1, block2 in neighbours:
            if len(block1) and len(block2):
                yield block1, block2

    def _cleanup(self):
        """ Cleanup blocking for further use (e.g. in pipeline)
        """
        self.minhasher = Minlsh()
        self.nb_elements = None


###############################################################################
# BLOCKING PIPELINE ###########################################################
###############################################################################
class PipelineBlocking(BaseBlocking):
    """ Pipeline multiple blocking techniques
    """

    def __init__(self, blockings, collect_stats=False):
        """ Build the blocking object

        Parameters
        ----------

        blockings: ordered list of blocking objects
        """
        self.blockings = blockings
        self.stored_blocks = []
        self.collect_stats = collect_stats
        self.stats = {}

    def _fit(self, refset, targetset):
        """ Internal fit of the pipeline """
        self._recursive_fit(
            refset, targetset, range(
                len(refset)), range(
                len(targetset)), 0)

    def _recursive_fit(self, refset, targetset, ref_index, target_index, ind):
        """ Recursive fit of the blockings.
        Blocks are stored in the stored_blocks attribute.
        """
        if ind < len(self.blockings) - 1:
            # There are other blockings after this one
            blocking = self.blockings[ind]
            blocking.cleanup()
            blocking.fit([refset[i] for i in ref_index],
                         [targetset[i] for i in target_index])
            for block1, block2 in blocking.iter_indice_blocks():
                ind_block1 = [ref_index[i] for i in block1]
                ind_block2 = [target_index[i] for i in block2]
                if self.collect_stats:
                    self.stats.setdefault(
                        ind, []).append(
                        (len(block1), len(block2)))
                self._recursive_fit(
                    refset, targetset, ind_block1, ind_block2, ind + 1)
        else:
            # This is the final blocking
            blocking = self.blockings[ind]
            blocking.cleanup()
            blocking.fit([refset[i] for i in ref_index],
                         [targetset[i] for i in target_index])
            for block1, block2 in blocking.iter_blocks():
                ind_block1 = [(ref_index[i], _id) for i, _id in block1]
                ind_block2 = [(target_index[i], _id) for i, _id in block2]
                if self.collect_stats:
                    self.stats.setdefault(
                        ind, []).append(
                        (len(block1), len(block2)))
                self.stored_blocks.append((ind_block1, ind_block2))

    def _iter_blocks(self):
        """ Internal iteration function over blocks
        """
        for block1, block2 in self.stored_blocks:
            if block1 and block2:
                yield block1, block2
