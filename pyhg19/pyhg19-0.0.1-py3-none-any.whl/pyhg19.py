#===============================================================================
# pyhg19.py
#===============================================================================

# Imports ======================================================================

import gzip
import os
import pydbsnp
import subprocess




# Constants ====================================================================

PATH = os.environ.get('PYHG19_PATH')
MASKED = os.environ.get('PYHG19_MASKED')
BOWTIE2_INDEX = os.environ.get('PYHG19_BOWTIE2_INDEX')




# Classes ======================================================================

class Coordinates():
    """The coordinates of a variant"""
    
    def __init__(self, chr, pos):
        self.chr = chr
        self.pos = pos
        self.tuple = chr, pos
    
    def __repr__(self):
        return 'Coordinates(chr={}, pos={})'.format(self.chr, self.pos)


class Variant():
    """The id and coordinates of a variant"""
    
    def __init__(self, id, chr, pos):
        self.id = id
        self.chr = chr
        self.pos = pos
        self.tuple = id, chr, pos
    
    def __repr__(self):
        return 'Variant(id={}, chr={}, pos={})'.format(
            self.id,
            self.chr,
            self.pos
        )




# Functions ====================================================================

def coord(rsid):
    """Get the coordinates and return them as an object"""
    
    chr, pos = coord_tuple(rsid)
    return Coordinates(chr, pos)


def coord_tuple(rsid):
    """Get the coordinates and return them as a tuple"""
    
    v = pydbsnp.Variant(id=rsid, reference_build='hg19')
    return (
        v.chrom.split('.')[0][-2:].replace('23', 'X').replace('24', 'Y').lstrip(
            '0'
        ),
        v.pos
    )


def rsid(chr, pos):
    """Get the rsid and return it as a string"""
    
    return pydbsnp.Variant(chr, pos, reference_build='hg19').id


def range(chr, start, end):
    """Generate all variants within a given genomic range"""
    
    with subprocess.Popen(
        (
            'tabix',
            pydbsnp.VCF_GRCH37,
            '{0}:{1}-{2}'.format(pydbsnp.CHROM_TO_HGVS['hg19'][chr], start, end)
        ),
        stdout=subprocess.PIPE
    ) as tabix:
        dbsnp_lines, _ = tabix.communicate()
    for dbsnp_line in dbsnp_lines.decode().splitlines():
        chr, pos, rsid, *rest = dbsnp_line.split('\t')
        yield Variant(
            rsid,
            chr.split('.')[0][-2:].replace('23', 'X').replace('24', 'Y').lstrip(
                '0'
            ),
            int(pos)
        )


def generate_coord_rsid_pairs(file):
    for line in file:
        if not line.startswith('#'):
            chr, pos, rsid, *rest = line.split()
            yield (
                (
                    chr.split('.')[0][-2:].replace('23', 'X').replace(
                        '24', 'Y'
                    ).lstrip('0'),
                    int(pos)
                ),
                rsid
            )


def coord_rsid_dict():
    """A dictionary containing coord: rsid pairs"""
    
    with gzip.open(pydbsnp.VCF_GRCH37, 'rt') as f:
        return dict(generate_coord_rsid_pairs(f))




# test =========================================================================

if __name__ == '__main__':
    rs10_coord = coord('rs10')
    print(
        'rs10 is on chromosome {0.chr} at position {0.pos}'.format(rs10_coord)
    )

    rs10_coord_tuple = coord_tuple('rs10')
    print(
        'rs10 is on chromosome {} at position {}'
        .format(rs10_coord_tuple[0], rs10_coord_tuple[1])
    )
    
    rs_something = rsid(chr=1, pos=10019)
    print(
        'The RSID of the variant on chromosome 1 at position 10019 is {}.'
        .format(rs_something)
    )
    
    try:
        coord('rs10a')
    except ValueError:
        print('error was handled')
