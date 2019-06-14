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
import pysam
import pyfaidx

from tempfile import NamedTemporaryFile
from hashlib import sha1
from wisestork.count import (get_chromosomes_from_header, reads_per_bin,
                             get_chromosomes_from_fasta, get_bins, count)


class TestFunctions:

    def test_sam_header(self):
        sam = pysam.AlignmentFile("test/data/test.bam")
        chroms = get_chromosomes_from_header(sam.header)
        assert len(chroms) == 1
        assert chroms[0][0] == "chrQ"
        assert chroms[0][1] == 500

    def test_fq_header(self):
        fa = pyfaidx.Fasta("test/data/chrQ.fasta")
        chroms = get_chromosomes_from_fasta(fa)
        assert len(chroms) == 1
        assert chroms[0][0] == "chrQ"
        assert chroms[0][1] == 500

    def test_count(self):
        sam = pysam.AlignmentFile("test/data/test.bam")
        bins = get_bins(500, 100)
        assert reads_per_bin(sam, "chrQ", bins[0]) == 40
        assert reads_per_bin(sam, "chrQ", bins[1]) == 52
        assert reads_per_bin(sam, "chrQ", bins[2]) == 34
        assert reads_per_bin(sam, "chrQ", bins[3]) == 42
        assert reads_per_bin(sam, "chrQ", bins[4]) == 26
        assert reads_per_bin(sam, "NotExist", bins[0]) == 0


class TestMain:

    def test_main(self):
        tmp_file = NamedTemporaryFile()
        count("test/data/test.bam", tmp_file.name, 100, "test/data/chrQ.fasta")
        output = b"".join(open(tmp_file.name, "rb").readlines())
        expected = b"".join(open("test/data/count.bed", "rb").readlines())
        assert sha1(output).hexdigest() == sha1(expected).hexdigest()

    def test_with_binfile(self):
        tmp_file = NamedTemporaryFile()
        count("test/data/test.bam", tmp_file.name, 100,
              "test/data/chrQ.fasta", "test/data/regions.bed")
        output = b"".join(open(tmp_file.name, "rb").readlines())
        expected = b"".join(open("test/data/count.bed", "rb").readlines())
        assert sha1(output).hexdigest() == sha1(expected).hexdigest()
