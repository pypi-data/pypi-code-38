#===============================================================================
# index.py
#===============================================================================

"""Index dbSNP VCFs by rsid"""



# Imports ======================================================================

import os.path
import subprocess

from argparse import ArgumentParser
from functools import partial
from multiprocessing import Pool

from pydbsnp.env import VCF_GRCH37, VCF_GRCH38, RSID_GRCH37, RSID_GRCH38




# Functions ====================================================================

def reformat_sort(
    input_vcf_path,
    output_rsid_path,
    quiet=False,
    temp_dir=None
):
    if not quiet:
        print(
            f'Reformatting database {input_vcf_path} and sorting by RSID. '
            'This will probably take a couple of hours. Reformatted and sorted '
            f'data will be written to {output_rsid_path}.'
        )
    with open(output_rsid_path, 'wb') as f:
        with subprocess.Popen(
            ('zcat', input_vcf_path), stdout=subprocess.PIPE
        ) as zcat:
            with subprocess.Popen(
                (
                    'awk', '-v', r'OFS=\t',
                    (
                        '!/##/ && !/#CHROM/ '
                        '{sub(/rs/, "", $3); print "rs", $3, $1, $2}'
                    ),
                ),
                stdin=zcat.stdout,
                stdout=subprocess.PIPE
            ) as awk:
                with subprocess.Popen(
                    (
                        'sort',
                        '-k2,2',
                        '-n',
                        '-T', temp_dir or os.path.dirname(output_rsid_path)
                    ),
                    stdin=awk.stdout,
                    stdout=subprocess.PIPE
                ) as sort:
                    subprocess.run(
                        ('bgzip', '--stdout'),
                        stdin=sort.stdout,
                        stdout=f
                    )
                

def index(rsid_file_path, quiet=False):
    if not quiet:
        print(f'Indexing {rsid_file_path}.')
    subprocess.run(
        (
            'tabix',
            '--csi',
            '--sequence', '1',
            '--begin', '2',
            '--end', '2', 
            rsid_file_path
        )
    )


def reformat_sort_index(
    input_vcf_path,
    output_rsid_path,
    quiet=False,
    temp_dir=None
):
    reformat_sort(
        input_vcf_path,
        output_rsid_path,
        quiet=quiet,
        temp_dir=temp_dir
    )
    index(output_rsid_path, quiet=False)
    

def parse_arguments():
    parser = ArgumentParser(description='index dbSNP VCF data by rsid')
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='suppress printed status updates'
    )
    parser.add_argument(
        '--processes',
        type=int,
        choices=(1, 2),
        default=1,
        help='set to 2 to index GRCh37 and GRCh38 data in parallel'
    )
    parser.add_argument(
        '--tmp-dir',
        metavar='<path/to/tmp/dir/>',
        help='directory for temporary files'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    if all(
        os.path.isfile(rsid)
        for vcf, rsid in ((VCF_GRCH37, RSID_GRCH37), (VCF_GRCH38, RSID_GRCH38))
        if os.path.isfile(vcf)
    ):
        decision = input(
            'Index files already exist, do you want to overwrite them? (y/N):'
        )
        if decision not in 'yY':
            return
    with Pool(processes=args.processes) as pool:
        pool.starmap(
            partial(
                reformat_sort_index,
                quiet=args.quiet,
                temp_dir=args.tmp_dir
            ),
            (
                (vcf, rsid)
                for vcf, rsid
                in ((VCF_GRCH37, RSID_GRCH37), (VCF_GRCH38, RSID_GRCH38))
                if os.path.isfile(vcf)
            )
        )
