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
import hashlib
from os import remove
from tempfile import NamedTemporaryFile
import pytest
from pyfaidx import Fasta

from wisestork.newref import (build_main_list, get_unique_bins,
                              ReferenceBinGenerator, newref)
from wisestork.utils import BedReader, BedLine


@pytest.fixture(scope="module")
def fuzzed_files():
    multipliers = [1.5, 2.0, 3.0, 3.5, 4.0]
    init = [x for x in BedReader("test/data/gc_correct.bed")]
    fs = []
    for multi in multipliers:
        tmp = NamedTemporaryFile(delete=False)
        t = [BedLine(x.chromosome, x.start, x.end, x.value*multi) for x in
             init]
        for z in t:
            tmp.write(bytes(z) + b"\n")
        tmp.close()
        fs.append(tmp)

    yield [x.name for x in fs]
    # teardown after this
    for f in fs:
        remove(f.name)


@pytest.fixture(scope="module")
def input_bins(fuzzed_files):
    inp = []
    for z in fuzzed_files:
        inp += [x for x in BedReader(z)]
    return inp


@pytest.fixture
def fasta():
    return Fasta("test/data/chrQ.fasta")


class TestFunctions:

    def test_get_unique_bins(self, fasta):
        bins = get_unique_bins(fasta, 100)
        assert len(bins) == 5
        for i, x in enumerate(bins):
            assert x.start == i*100
            assert x.end == (i+1)*100

    def test_build_main_list(self, input_bins, fasta):
        main = build_main_list(input_bins, 100, fasta)
        assert len(main) == 5
        assert main[0].start == 400
        assert main[1].start == 100
        assert main[2].start == 0
        assert main[3].start == 200
        assert main[4].start == 300
        main_w_f = build_main_list(input_bins, 100, fasta,
                                   "test/data/regions.bed")
        assert [x.start for x in main_w_f] == [x.start for x in main]


class TestReferenceBinGenerator:

    def test_init(self, fuzzed_files, fasta):
        ref1 = ReferenceBinGenerator(fuzzed_files, 5, fasta.filename, 100)
        assert len(ref1.get_all_bins()) == 5
        ref2 = ReferenceBinGenerator(fuzzed_files, 5, fasta.filename, 100,
                                     "test/data/regions.bed")
        assert len(ref2.get_all_bins()) == 5
        assert [x.start for x in ref1.get_all_bins()] == [x.start for x in
                                                          ref2.get_all_bins()]

    def test_get_nearest_and_filter(self, fuzzed_files, fasta):
        ref1 = ReferenceBinGenerator(fuzzed_files, 5, fasta.filename, 100)
        for i in range(5):
            a = ref1.get_nearest_at_idx(i)
            assert len(a) == 5
            filt = ref1.filter_bins(ref1.get_all_bins()[i], a)
            assert len(filt) == 4
        ref2 = ReferenceBinGenerator(fuzzed_files, 3, fasta.filename, 100)
        for i in range(5):
            a = ref2.get_nearest_at_idx(i)
            assert len(a) == 3
            filt = ref2.filter_bins(ref2.get_all_bins()[i], a)
            assert len(filt) == 2

    def test_iteration(self, fuzzed_files, fasta):
        ref1 = ReferenceBinGenerator(fuzzed_files, 5, fasta.filename, 100)
        refs = [x for x in ref1]
        assert len(refs) == 5


class TestMain:

    def test_main(self, fuzzed_files, fasta):
        o = NamedTemporaryFile(delete=False)
        o.close()
        newref(fuzzed_files, o.name, reference=fasta.filename, binsize=100,
               n_bins=5)
        m = hashlib.md5()
        with open(o.name) as handle:
            for l in handle:
                m.update(l.encode('utf-8'))
        assert m.hexdigest() == "a719c83e318f75c296bcf41adb50593a"
        remove(o.name)
