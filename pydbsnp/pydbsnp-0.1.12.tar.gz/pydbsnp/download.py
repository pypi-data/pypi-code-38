#===============================================================================
# download.py
#===============================================================================

"""Download VCF data from dbSNP"""



# Imports ======================================================================

import os.path

from argparse import ArgumentParser
from ftplib import FTP

from pydbsnp.env import FTP_BASENAME_GRCH37, FTP_BASENAME_GRCH38, BUILD_TO_VCF




# Constants ====================================================================

FTP_HOST = 'ftp.ncbi.nlm.nih.gov'
FTP_DIR = 'snp/latest_release/VCF'
BUILD_TO_FTP_BASENAME = {
    'hg19': FTP_BASENAME_GRCH37, 'GRCh37': FTP_BASENAME_GRCH37,
    'hg38': FTP_BASENAME_GRCH38, 'GRCh38': FTP_BASENAME_GRCH38
}
BUILD_TO_INT = {'hg19': 37, 'GRCh37':37, 'hg38': 38,'GRCh38': 38}




# Functions ====================================================================

def download(reference_build='GRCh38', quiet=False):
    if os.path.isfile(BUILD_TO_VCF[reference_build]):
        decision = input(
            f'A file already exists at {BUILD_TO_VCF[reference_build]}, do '
            'you want to overwrite it? (y/N):'
        )
        if decision not in 'yY':
            return

    if not quiet:
        print(
            'Downloading dbSNP data in VCF format '
            f'({reference_build} coordinates) to '
            f'{BUILD_TO_VCF[reference_build]}. '
            'This will probably take a few minutes.'
        )
    ftp = FTP(FTP_HOST)
    ftp.login()
    ftp.cwd(FTP_DIR)
    with open(BUILD_TO_VCF[reference_build], 'wb') as f:
        ftp.retrbinary(
            f'RETR {BUILD_TO_FTP_BASENAME[reference_build]}', f.write
        )
    if not quiet:
        print(
            f'Downloading tabix index to {BUILD_TO_VCF[reference_build]}.tbi.'
        )
    with open(f'{BUILD_TO_VCF[reference_build]}.tbi', 'wb') as f:
        ftp.retrbinary(
            f'RETR {BUILD_TO_FTP_BASENAME[reference_build]}.tbi', f.write
        )
    ftp.quit()
    if not quiet:
        print(f'Download complete.')


def parse_arguments():
    parser = ArgumentParser(description='download dbSNP VCF data')
    parser.add_argument(
        '--reference-build',
        choices=('hg19', 'GRCh37', 'hg38', 'GRCh38'),
        default='GRCh38',
        help='reference genome build'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='suppress printed status updates'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    download(reference_build=args.reference_build, quiet=args.quiet)
