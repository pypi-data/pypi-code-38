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
wisestork.gc
~~~~~~~~~~
:copyright: (c) 2016-2019 Sander Bollen
:license: GPL-3.0
"""

from Bio.SeqUtils import GC


def get_gc_for_bin(fasta, chromosome, bin):
    """
    Get number of GC bases in a region
    :param fasta: an instance of pyfaidx.Fasta
    :param chromosome: chromosome name
    :param bin: Bin namedtuple
    :return: integer
    """
    perc = GC(fasta[chromosome][bin.start:bin.end].seq)
    dist = bin.end-bin.start
    return int((perc*dist)/100)


def get_n_per_bin(fasta, chromosome, bin):
    """
    Get number of N bases in a region
    :param fasta: an instance of pyfaidx.Fasta
    :param chromosome: chromosome name
    :param bin: Bin namedtuple
    :return: integer
    """
    return fasta[chromosome][bin.start:bin.end].seq.upper().count('N')
