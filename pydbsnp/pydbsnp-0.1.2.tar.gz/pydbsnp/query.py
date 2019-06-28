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
HGVS_REGEX = re.compile(r'N._[0-9]{n}\.[0-9]+$')

CHROM_TO_HGVS = {
    'GRCh37': {
        'chr1': 'NC_000001.10',
        '1': 'NC_000001.10',
        1: 'NC_000001.10',
        'chr2': 'NC_000002.11',
        '2': 'NC_000002.11',
        2: 'NC_000002.11',
        'chr3': 'NC_000003.11',
        '3': 'NC_000003.11',
        3: 'NC_000003.11',
        'chr4': 'NC_000004.11',
        '4': 'NC_000004.11',
        4: 'NC_000004.11',
        'chr5': 'NC_000005.9',
        '5': 'NC_000005.9',
        5: 'NC_000005.9',
        'chr6': 'NC_000006.11',
        '6': 'NC_000006.11',
        6: 'NC_000006.11',
        'chr7': 'NC_000007.13',
        '7': 'NC_000007.13',
        7: 'NC_000007.13',
        'chr8': 'NC_000008.10',
        '8': 'NC_000008.10',
        8: 'NC_000008.10',
        'chr9': 'NC_000009.11',
        '9': 'NC_000009.11',
        9: 'NC_000009.11',
        'chr10': 'NC_000010.10',
        '10': 'NC_000010.10',
        10: 'NC_000010.10',
        'chr11': 'NC_000011.9',
        '11': 'NC_000011.9',
        11: 'NC_000011.9',
        'chr12': 'NC_000012.11',
        '12': 'NC_000012.11',
        12: 'NC_000012.11',
        'chr13': 'NC_000013.10',
        '13': 'NC_000013.10',
        13: 'NC_000013.10',
        'chr14': 'NC_000014.8',
        '14': 'NC_000014.8',
        14: 'NC_000014.8',
        'chr15': 'NC_000015.9',
        '15': 'NC_000015.9',
        15: 'NC_000015.9',
        'chr16': 'NC_000016.9',
        '16': 'NC_000016.9',
        16: 'NC_000016.9',
        'chr17': 'NC_000017.10',
        '17': 'NC_000017.10',
        17: 'NC_000017.10',
        'chr18': 'NC_000018.9',
        '18': 'NC_000018.9',
        18: 'NC_000018.9',
        'chr19': 'NC_000019.9',
        '19': 'NC_000019.9',
        19: 'NC_000019.9',
        'chr20': 'NC_000020.10',
        '20': 'NC_000020.10',
        20: 'NC_000020.10',
        'chr21': 'NC_000021.8',
        '21': 'NC_000021.8',
        21: 'NC_000021.8',
        'chr22': 'NC_000022.10',
        '22': 'NC_000022.10',
        22: 'NC_000022.10',
        'chrX': 'NC_000023.10',
        'X': 'NC_000023.10',
        23: 'NC_000023.10',
        'chrY': 'NC_000024.9',
        'Y': 'NC_000024.9',
        24: 'NC_000024.9',
        'chrM': 'NC_012920.1',
        'chrMT': 'NC_012920.1',
        'M': 'NC_012920.1',
        'MT': 'NC_012920.1',
        25: 'NC_012920.1'
    },
    'GRCh38': {
        'chr1': 'NC_000001.11',
        '1': 'NC_000001.11',
        1: 'NC_000001.11',
        'chr2': 'NC_000002.12',
        '2': 'NC_000002.12',
        2: 'NC_000002.12',
        'chr3': 'NC_000003.12',
        '3': 'NC_000003.12',
        3: 'NC_000003.12',
        'chr4': 'NC_000004.12',
        '4': 'NC_000004.12',
        4: 'NC_000004.12',
        'chr5': 'NC_000005.10',
        '5': 'NC_000005.10',
        5: 'NC_000005.10',
        'chr6': 'NC_000006.12',
        '6': 'NC_000006.12',
        6: 'NC_000006.12',
        'chr7': 'NC_000007.14',
        '7': 'NC_000007.14',
        7: 'NC_000007.14',
        'chr8': 'NC_000008.11',
        '8': 'NC_000008.1',
        8: 'NC_000008.11',
        'chr9': 'NC_000009.12',
        '9': 'NC_000009.12',
        9: 'NC_000009.12',
        'chr10': 'NC_000010.11',
        '10': 'NC_000010.11',
        10: 'NC_000010.11',
        'chr11': 'NC_000011.10',
        '11': 'NC_000011.10',
        11: 'NC_000011.10',
        'chr12': 'NC_000012.12',
        '12': 'NC_000012.12',
        12: 'NC_000012.12',
        'chr13': 'NC_000013.11',
        '13': 'NC_000013.11',
        13: 'NC_000013.11',
        'chr14': 'NC_000014.9',
        '14': 'NC_000014.9',
        14: 'NC_000014.9',
        'chr15': 'NC_000015.10',
        '15': 'NC_000015.10',
        15: 'NC_000015.10',
        'chr16': 'NC_000016.10',
        '16': 'NC_000016.10',
        16: 'NC_000016.10',
        'chr17': 'NC_000017.11',
        '17': 'NC_000017.11',
        17: 'NC_000017.11',
        'chr18': 'NC_000018.10',
        '18': 'NC_000018.10',
        18: 'NC_000018.10',
        'chr19': 'NC_000019.10',
        '19': 'NC_000019.10',
        19: 'NC_000019.10',
        'chr20': 'NC_000020.11',
        '20': 'NC_000020.11',
        20: 'NC_000020.11',
        'chr21': 'NC_000021.9',
        '21': 'NC_000021.9',
        21: 'NC_000021.9',
        'chr22': 'NC_000022.11',
        '22': 'NC_000022.11',
        22: 'NC_000022.11',
        'chrX': 'NC_000023.11',
        'X': 'NC_000023.11',
        23: 'NC_000023.11',
        'chrY': 'NC_000024.10',
        'Y': 'NC_000024.10',
        24: 'NC_000024.10',
        'chrM': 'NC_012920.1',
        'chrMT': 'NC_012920.1',
        'M': 'NC_012920.1',
        'MT': 'NC_012920.1',
        25: 'NC_012920.1'
    }
}
CHROM_TO_HGVS['hg19'] = CHROM_TO_HGVS['GRCh37']
CHROM_TO_HGVS['hg38'] = CHROM_TO_HGVS['GRCh38']





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
            self.chrom = (
                chrom_to_hgvs(chrom, reference_build=reference_build),
            )
            self.pos = (int(pos),)
        elif id and not (chrom or pos):
            rs_number = int(id.replace('rs', ''))
            self.chrom, self.pos = zip(
                *(
                    row.split()[2:]
                    for row in TabixFile(
                        BUILD_TO_RSID[reference_build],
                        index=f'{BUILD_TO_RSID[reference_build]}.csi'
                    ).fetch(
                        'rs', rs_number - 1, rs_number
                    )
                )
            )
            self.pos = tuple(int(p) for p in self.pos)
        
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
        self.chrom = self.chrom[0]
        self.pos = self.pos[0]
        self.id = self.id[0]
        self.ref = self.ref[0]
        self.alt = self.alt[0]
        self.info = self.info[0]
    
    def __repr__(self):
            return f"Varant(id='{self.id}')"




# Functions ====================================================================

def chrom_to_hgvs(chrom, reference_build='GRCh38'):
    if chrom in CHROM_TO_HGVS[reference_build].keys():
        return CHROM_TO_HGVS[reference_build][chrom]
    elif HGVS_REGEX.match(chrom):
        return chrom
    else:
        raise RuntimeError('invalid chromosome name')


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
