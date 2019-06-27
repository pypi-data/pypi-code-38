#===============================================================================
# query.py
#===============================================================================

"""query the dbSNP VCF data"""




# Imports ======================================================================

import re
import subprocess

from argparse import ArgumentParser
from pysam import TabixFile, VariantFile

from pydbsnp.env import BUILD_TO_VCF, BUILD_TO_RSID




# Constants ====================================================================

COORD_REGEX = re.compile('.+:[0-9]+$')
RSID_REGEX = re.compile('rs[1-9][0-9]+$')




# Functions ====================================================================

def rsid_to_coordinates(rsid, reference_build='GRCh38'):
    rs_number = rsid.replace('rs', '')
    with subprocess.Popen(
        (
            'tabix',
            BUILD_TO_RSID[reference_build],
            f'rs:{rs_number}-{rs_number}'
        ),
        stdout=subprocess.PIPE
    ) as tabix:
        for line in tabix.communicate()[0].decode().splitlines():
            yield line.split()[2:]


def parse_arguments():
    parser = ArgumentParser(description='query dbSNP VCF data')
    parser.add_argument(
        'variants',
        nargs='+',
        metavar='<rsid or chr:pos>',
        help='variant for which to query database'
    )
    parser.add_argument(
        '-r',
        '--reference-build',
        choices=('GRCh37', 'hg19', 'GRCh38', 'hg38'),
        default='GRCh38',
        help='reference build for coordinates'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    print(VariantFile(BUILD_TO_VCF[args.reference_build]).header)
    vcf = TabixFile(BUILD_TO_VCF[args.reference_build])
    for variant in args.variants:
        if COORD_REGEX.match(variant):
            chrom, pos = variant.split(':')
            pos = int(pos)
            for row in vcf.fetch(chrom, pos, pos):
                print(str(row))
        elif RSID_REGEX.match(variant):
            for chrom, pos in rsid_to_coordinates(
                variant,
                reference_build=args.reference_build
            ):
                for row in vcf.fetch(chrom, pos, pos):
                    print(str(row))
        else:
            raise RuntimeError('Improperly formatted query')
