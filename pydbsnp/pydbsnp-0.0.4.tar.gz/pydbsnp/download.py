#===============================================================================
# download.py
#===============================================================================

"""Download VCF data from dbSNP"""



# Imports ======================================================================

import argparse
import os
import os.path

from ftplib import FTP




# Constants ====================================================================

FTP_HOST = 'ftp.ncbi.nlm.nih.gov'
FTP_DIR = 'snp/latest_release/VCF'
VCF_FILENAME_GRCH37 = 'GCF_000001405.25.bgz'
VCF_FILENAME_GRCH38 = 'GCF_000001405.38.bgz'
VCF_DIR_DEFAULT = os.path.dirname(__file__)
BUILD_TO_FILENAME = {
    'hg19': VCF_FILENAME_GRCH37, 'GRCh37': VCF_FILENAME_GRCH37,
    'hg38': VCF_FILENAME_GRCH38, 'GRCh38': VCF_FILENAME_GRCH38
}
BUILD_TO_INT = {'hg19': 37, 'GRCh37':37, 'hg38': 38,'GRCh38': 38}




# Functions ====================================================================

def parse_arguments():
    parser = argparse.ArgumentParser(description='download dbSNP VCF data')
    parser.add_argument(
        '--reference-build',
        choices=('hg19', 'GRCh37', 'hg38', 'GRCh38'),
        default='GRCh38',
        help='reference genome build'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    dest = os.environ.get(
        f'PYDBSNP_VCF_{BUILD_TO_INT[args.reference_build]}',
        os.path.join(VCF_DIR_DEFAULT, BUILD_TO_FILENAME[args.reference_build])
    )
    print(
        'Downloading dbSNP data in VCF format '
        f'({args.reference_build} coordinates) '
        '(this will probably take a few minutes)'
    )
    ftp = FTP(FTP_HOST)
    ftp.login()
    ftp.cwd(FTP_DIR)
    with open(dest, 'wb') as f:
        ftp.retrbinary(
            f'RETR {BUILD_TO_FILENAME[args.reference_build]}', f.write
        )
    print('Downloading tabix index')
    with open(f'{dest}.tbi', 'wb') as f:
        ftp.retrbinary(
            f'RETR {BUILD_TO_FILENAME[args.reference_build]}.tbi', f.write
        )
    ftp.quit()
    print(f'Download complete, files saved in {os.path.dirname(dest)}')
