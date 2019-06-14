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
from pytest import fixture

from wisestork.gc_correct import filter_bin, correct
from wisestork.utils import BedLine, attempt_numeric


@fixture
def bedlines():
    with open("test/data/count.bed") as count_handle:
        bedlines = [BedLine(*map(attempt_numeric, x.split("\t"))) for x in
                    count_handle]
    return bedlines


@fixture
def fasta():
    return Fasta("test/data/chrQ.fasta")


class TestFunctions:
    def test_filter_bin(self, bedlines, fasta):
        assert all([filter_bin(x, fasta, 0.1, 0.001) for x in bedlines])
        assert all([not filter_bin(x, fasta, 0.1, 5) for x in bedlines])

    def test_correct(self, bedlines, fasta):
        assert all([x.value == 0 for x in correct(bedlines, fasta, frac_r=5)])
        corrected = correct(bedlines, fasta)
        for i in range(4):
            assert 0.9 < corrected[i].value < 1.1
        assert 0.4 < corrected[4].value < 0.6
