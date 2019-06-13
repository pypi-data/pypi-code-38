#    Copyright (C) 2016-2019  Sander Bollen
#
#    This file is part of wisestork
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see {http://www.gnu.org/licenses/}.

"""
wisestork.newref
~~~~~~~~~~~~~~
:copyright: (c) 2016-2019 Sander Bollen
:license: GPL-3.0
"""

import math
import numpy as np

from .utils import BedLine, get_bins, BedReader
from pyfaidx import Fasta


def get_unique_bins(fasta, binsize):
    """
    Get a list of unique bins (by position, not value!)
    :param fasta: pyfaidx.Fasta instance
    :return: bins
    """
    bins = []
    for contig in fasta:
        n = contig.name
        tmp_bins = get_bins(len(contig), binsize)
        bins += [BedLine(n, x[0], x[1], 0) for x in tmp_bins]

    return bins


def build_main_list(bins, binsize, reference, binfile=None):
    """
    Build main list of bins.
    All unique positions are selected
    Then the median value of all bins on those positions are calculated
    :param bins: list of bins
        order of this list should correspond to input files
        e.g. if 3 bins per file, this list looks like
        [1,2,3,1,2,3,1,2,3 ... ]
    :param binsize: binsize:
    :param reference: instance of pyfaidx.Fasta
    :return: list of bins (1 per position), sorted by median value
    """
    if not binfile:
        unique_positions = get_unique_bins(reference, binsize)
    else:
        reader = BedReader(binfile)
        unique_positions = [x for x in reader]
    median_bins = []
    for i, u in enumerate(unique_positions):
        working_bins = bins[i::len(unique_positions)]
        med = np.median([x.value for x in working_bins])
        median_bins.append(BedLine(u.chromosome, u.start, u.end, med))

    return sorted(median_bins, key=lambda x: x.value)


class ReferenceBinGenerator(object):
    """
    Iterator for generating reference bins
    Every item will be 2-tuple of (Bin, List[Bins])
    With the second item being similar bins
    """

    def __init__(self, inputs, n_bins, reference, binsize=int(1e6),
                 binfile=None):
        """
        Create instance of ReferenceBinGenerator
        :param inputs: list of paths to files of gc-corrected bedgraph files
        :param n_bins: number of neighbour bins to consider
        """
        self.inputs = inputs
        self.n_bins = n_bins
        self.fasta = Fasta(reference)
        self.binsize = binsize
        self.binfile = binfile
        self.__bins = self.get_all_bins()
        self.__idx = 0

    def get_all_bins(self):
        bins = []
        for inp in self.inputs:
            tmp_reader = BedReader(inp)
            bins += [x for x in tmp_reader]
        return build_main_list(bins, self.binsize, self.fasta, self.binfile)

    def __next__(self):
        if self.__idx == len(self.__bins):
            raise StopIteration
        nearest = self.get_nearest_at_idx(self.__idx)
        cur = self.__bins[self.__idx]
        filtered = self.filter_bins(cur, nearest)
        self.__idx += 1
        return cur, filtered

    def next(self):
        return self.__next__()

    def __iter__(self):
        return self

    def get_nearest_at_idx(self, idx):
        e_dist = len(self.__bins) - idx
        # starting edge; if distance from start less
        # or equal to half the window size
        if idx == 0 or 0 < idx <= self.n_bins//2:
            vals = self.__bins[:self.n_bins]
        # ending edge; if distance from end is less
        # or equal to half the window size
        elif e_dist <= self.n_bins//2:
            vals = self.__bins[-self.n_bins:]
        else:
            vals = self.__bins[idx-(self.n_bins//2):idx+int(math.ceil((self.n_bins/2)))]  # noqa
        return vals

    def filter_bins(self, target_bin, bins):
        """
        Filter a list of reference bins
        Bins to exclude:
         * target bin
         * Bins with value > 3x mean+stdev
         * Adjacent bins # TODO
        :param target_bin:
        :param bins:
        :return: filtered list of bins (may be empty)
        """
        ref_bins = [x for x in bins if x != target_bin]
        if len(ref_bins) == 0:
            return ref_bins

        stdev = np.std([x.value for x in ref_bins])
        mean = np.mean([x.value for x in ref_bins])
        non_outliers = [x for x in ref_bins if mean+(3*stdev) > x.value > mean-(3*stdev)]  # noqa
        return non_outliers


def newref(input_paths, output_path, reference, binsize, n_bins=250,
           binfile=None):
    """
    Create a new reference bed file
    :param input_paths: paths to gc-corrected BED files
    :param output_path: path to output bed file
    :param reference: path to reference Fasta
    :param binsize: binsize
    :param n_bins: number of neighbour bins to consider
    """
    gen = ReferenceBinGenerator(input_paths, n_bins, reference, binsize,
                                binfile)
    ohandle = open(output_path, "wb")
    for x in gen:
        chrom = x[0].chromosome
        start = x[0].start
        end = x[0].end
        references = []
        for record in x[1]:
            fmt = "{0},{1},{2}"
            if isinstance(record.chromosome, str):
                references.append(fmt.format(record.chromosome,
                                             record.start, record.end))
            else:
                references.append(fmt.format(record.chromosome.decode(),
                                             record.start, record.end))
        references = "|".join(references)

        if len(references) == 0:
            references = np.nan

        t = BedLine(chrom, start, end, references)
        ohandle.write(bytes(t) + b"\n")
