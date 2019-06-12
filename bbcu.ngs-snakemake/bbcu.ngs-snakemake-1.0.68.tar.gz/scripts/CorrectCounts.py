#!/usr/bin/env python

import argparse
import math

import pandas

__author__ = 'pmbarlev'

'''
Overview:
    Correct read counts on genes, to account for UMI-barcode clashes. This applies to Mars-seq experiments, where the positional data of the UMI is at the gene level (as opposed to at the locus level).

Input:
    An htseq-count counts file.

Output:
    A count file.

Arguments:
    --inputCounts:
    --outputCounts: The path to the output bam.
    --bcLength: loggging output (optional, default is std-err)

Usage:
    python CorrectCount.py \
    --inputCounts inCounts.txt \
    --outputCounts outCounts.txt
'''


def correct_single_count(n, b):
    if n == b: # Avoid log(0)
        n-=1
    return abs(-b * math.log(1 - n / float(b)))  # use abs to avoid -0.000


def umi_counts(counts_file, bc_length):
    counts0 = pandas.read_table(counts_file, header=None, names=["gene", "count"],keep_default_na=False) #In gtf of Derosofila there is "nan" gene. keep_default_na=False parameter cause to read this gens as regular string instead of NaN
    counts = counts0[~counts0.gene.str.startswith("__")]
    b = 4 ** bc_length

    try:
        counts = counts.assign(count_corrected=map(lambda count: correct_single_count(count, b), counts["count"]))
    except ValueError:
        raise ValueError("counts > # UMI options. Perhaps raw counts were input, instead of UMI counts.")
    return counts


def convert(x):
    try:
        return x.astype(int)
    except:
        return x


def write_counts_file(counts, out_file):
    counts = counts.apply(convert)
    counts.to_csv(out_file, sep="\t", header=False, index=False,
                  columns=["gene", "count_corrected"])  # float_format='%.1f')


###### Main ######
def parse_args():
    help_txt = "Correct UMI count for barcode clashing"
    parser = argparse.ArgumentParser(description=help_txt)
    parser.add_argument('--inputCounts', help='Input count file of UMIs per gene', required=True)
    parser.add_argument('--outputCounts', help='Output counts file', required=True)
    parser.add_argument('--bcLength', help='UMI barcode length', type=int, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    counts = umi_counts(args.inputCounts, args.bcLength)
    write_counts_file(counts, args.outputCounts)
