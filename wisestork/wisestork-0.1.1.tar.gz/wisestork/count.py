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
wisestork.count
~~~~~~~~~~~~~~
:copyright: (c) 2016-2019 Sander Bollen
:license: GPL-3.0
"""
import pysam

from .utils import get_bins, BedReader, BedLine


def reads_per_bin(bam_reader, chromosome, bin):
    """
    Number of reads per bin
    :param bam_reader: an instance of pysam.AlignmentFile
    :param chromosome: chromosome name
    :param bin: Bin namedtuple
    :return: integer
    """
    try:
        reads = bam_reader.count(chromosome, bin.start, bin.end)
    except ValueError:
        reads = 0

    return reads


def get_chromosomes_from_header(header):
    """
    Get list of chromosome names from bam headers
    :param header: bam header
    :return: list of tuples of (chromosome names, chromosome_length)
    """
    return [(x['SN'], x['LN']) for x in header['SQ']]


def get_chromosomes_from_fasta(fa):
    """
    Get chromosome names from fasta file
    :param fa: instance of pyfaidx.Fasta
    :return: list of tuples of (chromosome names, chromosome_lenght)
    """
    return [(x, len(fa[x])) for x in fa.keys()]


def count(input, output, binsize, reference, binfile=None):
    """
    Main function for counting reads per bin
    :param input: Path to input BAM
    :param output: path to output BED
    :param binsize: binsize
    :param reference: path to reference fasta
    """
    # TODO: check whether chromosome names in reference match those in bam file
    samfile = pysam.AlignmentFile(input, 'rb')
    chromosomes = get_chromosomes_from_header(samfile.header)
    with open(output, "wb") as ohandle:
        if binfile:
            bin_reader = BedReader(binfile)
            for bin in bin_reader:
                val = reads_per_bin(samfile, bin.chromosome, bin)
                bed = BedLine(bin.chromosome, bin.start, bin.end, val)
                ohandle.write(bytes(bed) + b"\n")
        else:
            for ch, ln in chromosomes:
                for bin in get_bins(ln, binsize):
                    val = reads_per_bin(samfile, ch, bin)
                    bed = BedLine(ch, bin.start, bin.end, val)
                    ohandle.write(bytes(bed) + b"\n")
