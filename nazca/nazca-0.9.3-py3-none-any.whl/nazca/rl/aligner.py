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
import time
import logging
from collections import defaultdict

from six import iteritems
from six.moves import xrange

from scipy import zeros
from scipy.sparse import lil_matrix

from nazca.utils.dataio import parsefile


###############################################################################
# UTILITY FUNCTIONS ###########################################################
###############################################################################
def iter_aligned_pairs(refset, targetset, global_mat,
                       global_matched, unique=True):
    """ Return the aligned pairs
    """
    if unique:
        for refid in global_matched:
            bestid, _ = sorted(global_matched[refid], key=lambda x: x[1])[0]
            ref_record = refset[refid]
            target_record = targetset[bestid]
            distance = global_mat[refid,
                                  bestid] if global_mat is not None else None
            yield (ref_record[0], refid), (target_record[0], bestid), distance
    else:
        for refid in global_matched:
            for targetid, _ in global_matched[refid]:
                ref_record = refset[refid]
                target_record = targetset[targetid]
                distance = global_mat[refid,
                                      targetid] if global_mat is not None else None
                yield (ref_record[0], refid), (target_record[0], targetid), distance


###############################################################################
# BASE ALIGNER OBJECT #########################################################
###############################################################################
class BaseAligner(object):

    def __init__(self, threshold, processings, normalize_matrix=False):
        self.threshold = threshold
        self.processings = processings
        self.normalize_matrix = normalize_matrix
        self.ref_normalizer = None
        self.target_normalizer = None
        self.target_normalizer = None
        self.blocking = None
        self.alignments_done = 0
        self.pairs_found = 0
        self.nb_comparisons = 0
        self.nb_blocks = 0
        self.refset_size = None
        self.targetset_size = None
        self.time = None
        self.logger = logging.getLogger('nazca.aligner')

    def register_ref_normalizer(self, normalizer):
        """ Register normalizers to be applied
        before alignment """
        self.ref_normalizer = normalizer

    def register_target_normalizer(self, normalizer):
        """ Register normalizers to be applied
        before alignment """
        self.target_normalizer = normalizer

    def register_blocking(self, blocking):
        self.blocking = blocking

    def apply_normalization(self, dataset, normalizer):
        if normalizer:
            return normalizer.normalize_dataset(dataset)
        return dataset

    def compute_distance_matrix(self, refset, targetset,
                                ref_indexes, target_indexes):
        """ Compute and return the global alignment matrix.
        For each `processing` a `Distancematrix` is built, then all the
        matrices are summed with their own weighting and the result is the global
        alignment matrix, which is returned.
        """
        distmatrix = zeros(
            (len(ref_indexes),
             len(target_indexes)),
            dtype='float32')
        for processing in self.processings:
            w = processing.weight
            distmatrix += w*processing.cdist(refset, targetset,
                                             ref_indexes, target_indexes)
        return distmatrix

    def threshold_matched(self, distmatrix):
        """ Return the matched elements within a dictionnary,
        each key being the indice from X, and the corresponding
        values being a list of couple (indice from Y, distance)
        """
        match = defaultdict(list)
        if self.normalize_matrix:
            distmatrix /= distmatrix.max()
        ind = (distmatrix <= self.threshold).nonzero()
        indrow = ind[0].tolist()
        indcol = ind[1].tolist()
        for (i, j) in zip(indrow, indcol):
            match[i].append((j, distmatrix[i, j]))
        return match

    def _get_match(self, refset, targetset, ref_indexes=None,
                   target_indexes=None):
        # Build items
        ref_indexes = ref_indexes or xrange(len(refset))
        target_indexes = target_indexes or xrange(len(targetset))
        # Apply alignments
        mat = self.compute_distance_matrix(refset, targetset,
                                           ref_indexes=ref_indexes,
                                           target_indexes=target_indexes)
        matched = self.threshold_matched(mat)
        # Reapply matched to global indexes
        new_matched = {}
        for k, values in iteritems(matched):
            new_matched[ref_indexes[k]] = [
                (target_indexes[i], d) for i, d in values]
        return mat, new_matched

    def align(self, refset, targetset, get_matrix=True):
        """ Perform the alignment on the referenceset
        and the targetset
        """
        start_time = time.time()
        refset = self.apply_normalization(refset, self.ref_normalizer)
        targetset = self.apply_normalization(targetset, self.target_normalizer)
        self.refset_size = len(refset)
        self.targetset_size = len(targetset)
        # If no blocking
        if not self.blocking:
            return self._get_match(refset, targetset)
        # Blocking == conquer_and_divide
        global_matched = {}
        global_mat = lil_matrix((len(refset), len(targetset)))
        self.blocking.fit(refset, targetset)
        for refblock, targetblock in self.blocking.iter_blocks():
            self.nb_blocks += 1
            ref_index = [r[0] for r in refblock]
            target_index = [r[0] for r in targetblock]
            self.nb_comparisons += len(ref_index) * len(target_index)
            _, matched = self._get_match(
                refset, targetset, ref_index, target_index)
            for k, values in iteritems(matched):
                subdict = global_matched.setdefault(k, set())
                for v, d in values:
                    subdict.add((v, d))
                    self.alignments_done += 1
                    if get_matrix:
                        # XXX avoid issue in sparse matrix
                        global_mat[k, v] = d or 10**(-10)
        self.time = time.time() - start_time
        return global_mat, global_matched

    def get_aligned_pairs(self, refset, targetset,
                          unique=True, use_distance=True):
        """ Get the pairs of aligned elements
        """
        if not refset or not targetset:
            return
        global_mat, global_matched = self.align(
            refset, targetset, get_matrix=use_distance)
        for pair in iter_aligned_pairs(
                refset, targetset, global_mat, global_matched, unique):
            self.pairs_found += 1
            yield pair
        self.log_infos()

    def align_from_files(self, reffile, targetfile,
                         ref_indexes=None, target_indexes=None,
                         ref_encoding=None, target_encoding=None,
                         ref_separator='\t', target_separator='\t',
                         get_matrix=True):
        """ Align data from files

        Parameters
        ----------

        reffile: name of the reference file

        targetfile: name of the target file

        ref_encoding: if given (e.g. 'utf-8' or 'latin-1'), it will
                      be used to read the files.

        target_encoding: if given (e.g. 'utf-8' or 'latin-1'), it will
                         be used to read the files.

        ref_separator: separator of the reference file

        target_separator: separator of the target file
        """
        refset = parsefile(reffile, indexes=ref_indexes,
                           encoding=ref_encoding, delimiter=ref_separator)
        targetset = parsefile(targetfile, indexes=target_indexes,
                              encoding=target_encoding, delimiter=target_separator)
        return self.align(refset, targetset, get_matrix=get_matrix)

    def get_aligned_pairs_from_files(self, reffile, targetfile,
                                     ref_indexes=None, target_indexes=None,
                                     ref_encoding=None, target_encoding=None,
                                     ref_separator='\t', target_separator='\t',
                                     unique=True):
        """ Get the pairs of aligned elements
        """
        refset = parsefile(reffile, indexes=ref_indexes,
                           encoding=ref_encoding, delimiter=ref_separator)
        targetset = parsefile(targetfile, indexes=target_indexes,
                              encoding=target_encoding, delimiter=target_separator)
        if not refset or not targetset:
            return
        global_mat, global_matched = self.align(
            refset, targetset, get_matrix=False)
        for pair in iter_aligned_pairs(
                refset, targetset, global_mat, global_matched, unique):
            yield pair

    def log_infos(self):
        """ Display some info on the aligner process
        """
        self.logger.info('Computation time : %s' % self.time)
        self.logger.info('Size reference set : %s' % self.refset_size)
        self.logger.info('Size target set : %s' % self.targetset_size)
        self.logger.info('Comparisons done : %s' % self.nb_comparisons)
        self.logger.info('Alignments done : %s' % self.alignments_done)
        self.logger.info('Pairs found : %s' % self.pairs_found)
        self.logger.info('Ratio reference set/alignments done : %s'
                         % (self.alignments_done / float(self.refset_size)))
        self.logger.info('Ratio target set/alignments done : %s'
                         % (self.alignments_done / float(self.targetset_size)))
        self.logger.info('Ratio reference set/pairs found : %s'
                         % (self.pairs_found / float(self.refset_size)))
        self.logger.info('Ratio target set/pairs found : %s'
                         % (self.pairs_found / float(self.targetset_size)))
        self.logger.info('Maximum comparisons : %s'
                         % (self.refset_size * self.targetset_size))
        self.logger.info('Number of blocks : %s' % self.nb_blocks)
        if self.nb_blocks:
            self.logger.info('Ratio comparisons/block : %s'
                             % (float(self.nb_comparisons) / self.nb_blocks))
        self.logger.info('Blocking reduction : %s'
                         % (self.nb_comparisons / float(self.refset_size * self.targetset_size)))


###############################################################################
# PIPELINE ALIGNER OBJECT ####################################################
###############################################################################
class PipelineAligner(object):
    """ This pipeline will perform iterative alignments, removing each time
    the aligned results from the previous aligner.
    """

    def __init__(self, aligners):
        self.aligners = aligners
        self.pairs = {}
        self.nb_comparisons = 0
        self.nb_blocks = 0
        self.alignments_done = 0
        self.pairs_found = 0
        self.refset_size = None
        self.targetset_size = None
        self.time = None
        self.logger = logging.getLogger('nazca.aligner')

    def get_aligned_pairs(self, refset, targetset, unique=True):
        """ Get the pairs of aligned elements
        """
        if not refset or not targetset:
            return
        start_time = time.time()
        ref_index = range(len(refset))
        target_index = range(len(targetset))
        self.refset_size = len(refset)
        self.targetset_size = len(targetset)
        seen_refset = set()
        # Iteration over aligners
        for ind_aligner, aligner in enumerate(self.aligners):
            # Perform alignment
            _refset = [refset[i] for i in ref_index]
            _targetset = [targetset[i] for i in target_index]
            for pair in aligner.get_aligned_pairs(_refset, _targetset, unique):
                self.pairs_found += 1
                pair = ((pair[0][0], ref_index[pair[0][1]]),
                        (pair[1][0], target_index[pair[1][1]]))
                yield pair
                seen_refset.add(pair[0][1])
            # Store stats
            self.nb_blocks += aligner.nb_blocks
            self.nb_comparisons += aligner.nb_comparisons
            # Update indexes if necessary
            # For now, we remove all the reference set that are already matched
            if ind_aligner < len(self.aligners) - 1:
                # There are other aligners after this one
                ref_index = [i for i in ref_index if i not in seen_refset]
        self.time = time.time() - start_time
        self.log_infos()

    def log_infos(self):
        """ Display some info on the aligner process
        """
        self.logger.info('Computation time : %s' % self.time)
        self.logger.info('Size reference set : %s' % self.refset_size)
        self.logger.info('Size target set : %s' % self.targetset_size)
        self.logger.info('Comparisons done : %s' % self.nb_comparisons)
        self.logger.info('Alignments done : %s' % self.alignments_done)
        self.logger.info('Pairs found : %s' % self.pairs_found)
        self.logger.info('Ratio reference set/alignments done : %s'
                         % (self.alignments_done / float(self.refset_size)))
        self.logger.info('Ratio target set/alignments done : %s'
                         % (self.alignments_done / float(self.targetset_size)))
        self.logger.info('Ratio reference set/pairs found : %s'
                         % (self.pairs_found / float(self.refset_size)))
        self.logger.info('Ratio target set/pairs found : %s'
                         % (self.pairs_found / float(self.targetset_size)))
        self.logger.info('Maximum comparisons : %s'
                         % (self.refset_size * self.targetset_size))
        self.logger.info('Number of blocks : %s' % self.nb_blocks)
        if self.nb_blocks:
            self.logger.info('Ratio comparisons/block : %s'
                             % (float(self.nb_comparisons) / self.nb_blocks))
        self.logger.info('Blocking reduction : %s'
                         % (self.nb_comparisons / float(self.refset_size * self.targetset_size)))
