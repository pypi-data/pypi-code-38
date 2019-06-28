#===============================================================================
# query.py
#===============================================================================

"""query the dbSNP VCF data"""




# Imports ======================================================================

import re

from argparse import ArgumentParser
from pysam import TabixFile, VariantFile

from pydbsnp.env import BUILD_TO_VCF, BUILD_TO_RSID




# Constants ====================================================================

COORD_REGEX = re.compile('.+:[0-9]+$')
RSID_REGEX = re.compile('rs[1-9][0-9]+$')




# Classes ======================================================================

class GeneralizedVariant():

    def __init__(
        self,
        chrom=None,
        pos=None,
        id=None,
        reference_build='GRCh38'
    ):
        if chrom and pos and not id:
            self.chrom, self.pos = (chrom,), (pos,)
        elif id and not (chrom or pos):
            rs_number = int(id.replace('rs', ''))
            self.chrom, self.pos = zip(
                *(
                    row.split()[2:]
                    for row in TabixFile(BUILD_TO_RSID[reference_build]).fetch(
                        'rs', rs_number - 1, rs_number
                    )
                )
            )
        
        _, _, self.id, self.ref, self.alt, _, _, self.info = zip(
            *(
                row.split()
                for chrom, pos in zip(self.chrom, self.pos)
                for row in TabixFile(BUILD_TO_VCF[reference_build]).fetch(
                    chrom, pos - 1, pos
                )
            )
        )

    def __repr__(self):
        return f"GeneralizedVarant(id='{self.id[0]}')"


class Variant(GeneralizedVariant):
    
    def __init__(
        self,
        chrom=None,
        pos=None,
        id=None,
        reference_build='GRCh38'
    ):
        super().__init__(
            chrom=chrom,
            pos=pos,
            id=id,
            reference_build=reference_build
        )
        for field in (
            self.chrom, self.pos, self.id, self.ref, self.alt, self.info
        ):
            field = field[0]

    def __repr__(self):
            return f"Varant(id='{self.id}')"




# Functions ====================================================================

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
    vcf_file = TabixFile(BUILD_TO_VCF[args.reference_build])
    rsid_file = TabixFile(
        BUILD_TO_RSID[args.reference_build],
        index=f'{BUILD_TO_RSID[args.reference_build]}.csi'
    )
    def rsid_to_coordinates(rsid):
        rs_number = int(rsid.replace('rs', ''))
        for row in rsid_file.fetch('rs', rs_number - 1, rs_number):
            chrom, pos = row.split()[2:]
            yield chrom, int(pos)
    for variant in args.variants:
        if COORD_REGEX.match(variant):
            chrom, pos = variant.split(':')
            pos = int(pos)
            for row in vcf_file.fetch(chrom, pos - 1, pos):
                print(row)
        elif RSID_REGEX.match(variant):
            for chrom, pos in rsid_to_coordinates(variant):
                for row in vcf_file.fetch(chrom, pos - 1, pos):
                    print(row)
        else:
            raise RuntimeError('Improperly formatted query')
