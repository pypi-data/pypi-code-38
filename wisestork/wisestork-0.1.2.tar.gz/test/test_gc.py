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
from pyfaidx import Fasta

from wisestork.gc import get_n_per_bin, get_gc_for_bin
from wisestork.utils import get_bins


class TestFunctions:

    def test_n_per_bin(self):
        fa = Fasta("test/data/chrQ.fasta")
        bins = get_bins(500, 100)
        for bin in bins:
            assert get_n_per_bin(fa, 'chrQ', bin) == 0

    def test_get_gc_for_bin(self):
        fa = Fasta("test/data/chrQ.fasta")
        bins = get_bins(500, 100)
        assert get_gc_for_bin(fa, "chrQ", bins[0]) == 47
        assert get_gc_for_bin(fa, "chrQ", bins[1]) == 50
        assert get_gc_for_bin(fa, "chrQ", bins[2]) == 54
        assert get_gc_for_bin(fa, "chrQ", bins[3]) == 58
        assert get_gc_for_bin(fa, "chrQ", bins[4]) == 50
