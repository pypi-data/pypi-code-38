#!python
""" variant benchmark tools """

import os
import sys
import argparse
import subprocess as sp
import pandas as pd
from vbtools import vbtools as vb


def allele_comparison(vcf, bench, prefix):
    """ allele level consensus """
    print(" + Perform allele level comparison.\n")
    # merge variant ID tables
    vartab = vb.get_variant_table(
        vb.get_var_ids(vcf, prefix),
        vb.get_var_ids(bench, os.path.join('bench')))
    vartab.to_csv(prefix+'.all_vars.txt', sep='\t')
    count_table = (vartab[prefix] - vartab['bench']).value_counts()
    count_table.index = count_table.index.astype('int32')
    for i in [-1, 0, 1]:
        if i not in count_table.index:
            count_table[i] = 0
    count_table = count_table.sort_index().reset_index()
    count_table.index = ['test_unique', 'shared', 'bench_unique']
    count_table.to_csv(prefix+'.allele_comp.tsv', sep='\t')


def sample_comparison(vcf, bench, prefix):
    """ consensus across samples """
    print(" + Sample leve comparison")
    return


def main(vcf, bench, prefix):
    vb.format_check(vcf, bench)
    prc_vcf = vb.preprocess_vcf(vcf, prefix)
    allele_comparison(prc_vcf, bench, prefix)
    # sample_comparison(prc_vcf, bench)
    print(" + Done.")

# TODO:
# - support mini-representation of INDELs
# - Add support for diploid

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    # required arguments
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '-v', '--vcf', required=True, help='Input VCFs for comparison')
    required.add_argument(
        '-b', '--benchmark', required=True,
        help="Data set to benchmark against"
    )

    # optional arguments
    # parser.add_argument(
    #     '--ploidy', help="VCF ploidy, 1 for haploid and 2 for diploid",
    #     default=1, type=int
    # )
    parser.add_argument(
        '-p', '--prefix', help="Output file", default='varbench'
    )

    args = parser.parse_args()
    main(args.vcf, args.benchmark, args.prefix)
