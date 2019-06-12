# Tests for CLI tools of hicstuff
# Commands are simply run to test for crashes.
# TODO: add tests to check for output contents
from hicstuff import commands as hcmd
import os
import shutil as su

# Use global variables for input files
MAT = "test_data/abs_fragments_contacts_weighted.txt"
FRAG = "test_data/fragments_list.txt"
CHROM = "test_data/info_contigs.txt"
OUT = "test_cli"
os.makedirs(OUT, exist_ok=True)


def test_view():
    args = (
        "-b 500bp -c Reds -d -f {0} -T log2 -n -t 1 -m 0.98 -r seq2:100-10000 "
        + "-o {1}/test.png {2}"
    ).format(FRAG, OUT, MAT)
    proc = hcmd.View(args.split(" "), {})
    proc.execute()


def test_pipeline():
    args = (
        "-e DpnII -t 1 -F -D -d -i -n -P test -o {0} -g test_data/genome/seq "
        + "test_data/sample.reads_for.fastq.gz test_data/sample.reads_rev.fastq.gz"
    ).format(OUT)
    proc = hcmd.Pipeline(args.split(" "), {})
    proc.execute()


def test_rebin():
    args = "-b 1kb -f {0} -c {1} -o {2} {3}".format(FRAG, CHROM, OUT, MAT)
    proc = hcmd.Rebin(args.split(" "), {})
    proc.execute()


def test_convert():
    args = "-f {0} -c {1} -o {2} {3}".format(FRAG, CHROM, OUT, MAT)
    proc = hcmd.Convert(args.split(" "), {})
    proc.execute()


def test_distancelaw():
    args = (
        "-a -o test.png -d test_data/distance_law.txt"
        + " -c test_data/centromeres.txt -b 10000 -r 1000 -B 1.1"
    )
    proc = hcmd.Distancelaw(args.split(" "), {})
    proc.execute()


def test_distance_law_2():
    args = (
        "-p test_data/valid_idx_filtered.pairs -f {0} -C"
        + " -O {1}/test_distance_law.txt -i 500 -s 45000"
    ).format(FRAG, OUT)
    proc = hcmd.Distancelaw(args.split(" "), {})
    proc.execute()


def test_iteralign():
    args = (
        "-g test_data/genome/seq -t 1 -T tmp -l 30"
        + " -o {0}/test.sam test_data/sample.reads_for.fastq.gz"
    ).format(OUT)
    proc = hcmd.Iteralign(args.split(" "), {})
    proc.execute()


def test_digest():
    args = "-e DpnII -p -f {0} -o {0} test_data/genome/seq.fa".format(OUT)
    proc = hcmd.Digest(args.split(" "), {})
    proc.execute()


def test_filter():
    args = "-f {0}, -p test_data/valid_idx.pairs {0}/valid_idx_filtered.pairs".format(
        OUT
    )
    proc = hcmd.Filter(args.split(" "), {})
    proc.execute()


def test_scalogram():
    args = "-C viridis -n -t 1 -o {0}/scalo.png {1}".format(OUT, MAT)
    proc = hcmd.Scalogram(args.split(" "), {})
    proc.execute()


def test_subsample():
    args = "-p 0.5 {0} {1}/subsampled.tsv".format(MAT, OUT)
    proc = hcmd.Subsample(args.split(" "), {})
    proc.execute()


# su.rmtree(OUT)
