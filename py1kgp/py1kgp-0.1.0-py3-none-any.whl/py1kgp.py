#!/usr/bin/env python3
#===============================================================================
# py1kgp.py
#===============================================================================

# Imports ======================================================================

import gzip
import os.path
import pyhg19
import re
import subprocess




# Constants ====================================================================

DIR = os.environ.get('PY1KGP_DIR')
PATH_FORMAT = os.path.join(
    DIR,
    'ALL.chr{}.phase3_shapeit2_mvncall_integrated_{}.20130502.genotypes.vcf.gz'
)
PANEL_PATH = os.path.join(DIR, 'integrated_call_samples_v3.20130502.ALL.panel')
POPULATION_CODES = {
    'AFR', 'AMR', 'EAS', 'EUR', 'SAS', 'ACB', 'ASW', 'BEB', 'CDX', 'CEU',
    'CHB', 'CHS', 'CLM', 'ESN', 'FIN', 'GBR', 'GIH', 'GWD', 'IBS', 'ITU',
    'JPT', 'KHV', 'LWK', 'MSL', 'MXL', 'PEL', 'PJL', 'PUR', 'STU', 'TSI',
    'YRI'
}
MAF_RE = {
    pop: re.compile('{}_AF=(.*?)[,;]'.format(pop)) for pop in {
        'AFR', 'AMR', 'EAS', 'EUR', 'SAS'
    }
}
MAF_RE['ALL'] = re.compile(';AF=(.*?)[,;]')
DEFAULT_DICTS_FILE_PATH = DIR + '/1kgp.info.fixed.txt.gz'




# Classes ======================================================================

class Variant():
    """A variant.
    
    Parameters
    ----------
    chrom : str or int
        chromosome of the variant
    pos : int
        position of the variant
    id : str
        rsid of the variant
    
    Attributes
    ----------
    chrom : str
        chromosome identifier of the variant
    pos : int
        position of the variant
    id : str
        rsid of the variant
    ref : str
        reference allele of the variant
    alt : str
        alternate allele of the variant
    qual : int
        quality score
    filter : str
        FILTER column from VCF
    info : str
        info column from the dbSNP vcf
    """
    
    def __init__(self, chrom=None, pos=None, id=None):
        if id:
            chrom, pos = pyhg19.coord_tuple(id)
        elif isinstance(chrom, str):
            if chrom[0] == 'r':
                chrom, pos = pyhg19.coord_tuple(chrom)
        elif not all((chrom, pos)):
            raise ValueError('Ill-defined input')
        chrom = str(chrom).replace('chr', '')
        with subprocess.Popen(
            (
                'tabix', '-h',
                get_vcf_file_path(chrom),
                '{0}:{1}-{1}'.format(chrom, pos)
            ),
            stdout=subprocess.PIPE
        ) as tabix:
            tabix_output = tuple(
                line
                for line in tabix.communicate()[0].decode().split('\n')
                if (line[:2] != '##')
            )
        if len(tabix_output) < 3:
            raise RuntimeError(
                'Variant at {}:{} not found in 1KGP'.format(chrom, pos)
            )
        samples = tabix_output[0].split('\t')[10:]
        (
            self.chrom, self.pos, self.id, self.ref, self.alt, self.qual,
            self.filter, info_column, _, *genotypes
        ) = tabix_output[-2].split('\t')
        self.info = dict(
            item.split('=') for item in info_column.split(';') if ('=' in item)
        )
        self.info['EX_TARGET'] = 'EX_TARGET' in info_column
        self.genotype = dict(
            zip(
                samples,
                (
                    tuple(
                        int(allele) for allele in genotype.split('|')
                    ) for genotype in genotypes
                )
            )
        )
    
    def __repr__(self):
        return (
            ',\n'
            .join(
                (
                    'kgp.Variant(',
                    '    CHROM={}',
                    '    POS={}',
                    '    ID={}',
                    '    REF={}',
                    '    ALT={}',
                    '    QUAL={}',
                    '    FILTER={}',
                    ')'
                )
            )
            .format(
                self.chrom, self.pos, self.id, self.ref, self.alt, self.qual,
                self.filter
            )
        )




# Functions ====================================================================

def get_vcf_file_path(chrom):
    if chrom == 'M':
        chrom = 'MT'
    return PATH_FORMAT.format(chrom, ('v1b' if chrom == 'X' else 'v5a'))


def slice_vcf(chrom, start: int, end: int, samples=None):
    """Get a slice of a 1KGP VCF as a bytes object

    Parameters
    ----------
    chrom : str or int
        chromosome of the slice
    start : int
        start position
    end : int
        end position
    samples
        population or samples to include
    
    Returns
    -------
    bytes
        the sliced VCF file
    """

    if chrom == 'M':
        chrom = 'MT'
    with subprocess.Popen(
            (
                'tabix', '-h',
                get_vcf_file_path(chrom),
                '{}:{}-{}'.format(chrom, start, end)
            ),
            stdout=subprocess.PIPE
        ) as tabix:
            if not samples:
                return tabix.communicate()[0]
            else:
                if samples in POPULATION_CODES:
                    samples_flag = '-s'
                    samples_arg = ','.join(get_panel(samples))
                elif os.path.isfile(samples):
                    samples_flag = '-S'
                    samples_arg = samples
                else:
                    samples_flag = '-s'
                    samples_arg = (
                        samples if isinstance(samples, str) else ','.join(
                            samples
                        )
                    )
                with subprocess.Popen(
                    (
                        'bcftools',
                        'view',
                        samples_flag, 
                        samples_arg
                    ),
                    stdin=tabix.stdout,
                    stdout=subprocess.PIPE
                ) as bcftools:
                    return bcftools.communicate()[0]


def fast_maf(chrom, pos, population='ALL'):
    """Originally an attempt to efficiently look up MAFs. Actually not very
    fast, apparently...
    
    Parameters
    ----------
    chrom : str or int
        chromosome of variant to look up
    pos : int
        position of variant to look up
    population : str
        population for which to look up MAF
    
    Returns
    -------
    str
        MAF info for the variant
    """
    
    with subprocess.Popen(
            (
                'tabix',
                get_vcf_file_path(chrom),
                '{0}:{1}-{1}'.format(chrom, pos)
            ),
            stdout=subprocess.PIPE
        ) as tabix:
            try:
                return (
                    MAF_RE[population]
                    .search(tabix.communicate()[0].decode().split('\n')[-2])
                    .group(1)
                )
            except IndexError:
                return None


def fast_genotypes(chrom, pos: int, samples):
    """Efficiently look up genotypes for a variant

    Parameters
    ----------
    chrom: str or int
        chromosome of the variant
    pos : int
        position of the variant
    samples
        iterable or comma-delimited string of samples to look up
    
    Returns
    -------
    list
        the genotypes
    """

    with subprocess.Popen(
            (
                'tabix', '-h',
                get_vcf_file_path(chrom),
                '{0}:{1}-{1}'.format(chrom, pos)
            ),
            stdout=subprocess.PIPE
        ) as tabix:
            with subprocess.Popen(
                (
                    'bcftools',
                    'view',
                    '-s', 
                    samples if isinstance(samples, str) else ','.join(samples)
                ),
                stdin=tabix.stdout,
                stdout=subprocess.PIPE
            ) as bcftools:
                return (
                    bcftools
                    .communicate()[0]
                    .decode()
                    .split('\n')[-2]
                    .split('\t')[9:]
                )


def get_panel(population_code):
    with open(PANEL_PATH, 'r') as f:
        panel = tuple(
            line.split()[0] for line in f if population_code in {
                line.split()[1], line.split()[2]
            }
        )
    return panel


def generate_dicts_data(file_path=None):
    if not file_path:
        file_path = DEFAULT_DICTS_FILE_PATH
    with (
        gzip.open(file_path, 'rt')
        if file_path[-3:] == '.gz' else open(file_path, 'r')
    ) as f:
        for line in f:
            yield line.rstrip('\n').split('\t')


def dicts(file_path=None):
    chromosome_dict, position_dict, maf_dict = {}, {}, {}
    for chrom, pos, rsid, maf in generate_dicts_data(file_path=file_path):
        chromosome_dict[rsid] = chrom
        position_dict[rsid] = pos
        maf_dict[rsid] = maf
    return chromosome_dict, position_dict, maf_dict


def all_coordinates(file_path=None):
    return {
        (chrom, int(pos))
        for chrom, pos, rsid, maf in generate_dicts_data(file_path=file_path)
    }


def coordinate_rsid_dict(file_path=None):
    return {
        (chrom, int(pos)): rsid
        for chrom, pos, rsid, maf in generate_dicts_data(file_path=file_path)
    }
