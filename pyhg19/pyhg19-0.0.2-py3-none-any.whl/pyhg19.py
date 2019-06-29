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
    """The coordinates of a variant
    
    Parameters
    ----------
    chr : str
        chromosome
    pos : int
        position
    
    Attributes
    ----------
    chr : str
        chromosome
    pos : int
        position
    tuple : tuple
        (chromosome, position)
    """
    
    def __init__(self, chr: str, pos: int):
        self.chr = chr
        self.pos = pos
        self.tuple = chr, pos
    
    def __repr__(self):
        return 'Coordinates(chr={}, pos={})'.format(self.chr, self.pos)


class Variant():
    """The ID and coordinates of a variant
    
    Parameters
    ----------
    id : str
        rsid of the variant
    chr : str
        chromosome of the variant
    pos : int
        position of the variant
    
    Attributes
    ----------
    id : str
        rsid of the variant
    chr : str
        chromosome of the variant
    pos : int
        position of the variant
    tuple : tuple
        (id, chromosome, position)
    """
    
    def __init__(self, id: str, chr: str, pos: int):
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

def coord(rsid: str):
    """Get the coordinates and return them as an object

    Parameters
    ----------
    rsid : str
        the rsid of a variant

    Returns
    -------
    Coordinates
        the variant's coordinates
    """
    
    chr, pos = coord_tuple(rsid)
    return Coordinates(chr, pos)


def coord_tuple(rsid: str):
    """Get the coordinates and return them as a tuple

    Parameters
    ----------
    rsid : str
        the rsid of a variant

    Returns
    -------
    tuple
        the variant's coordinates
    """
    
    v = pydbsnp.Variant(id=rsid, reference_build='hg19')
    return (
        v.chrom.split('.')[0][-2:].replace('23', 'X').replace('24', 'Y').lstrip(
            '0'
        ),
        v.pos
    )


def rsid(chr: str, pos: int):
    """Get the rsid and return it as a string

    Parameters
    ----------
    chr : str
        chromosome
    pos : int
        position
    
    Returns
    -------
    str
        the RSID
    """
    
    return pydbsnp.Variant(chr, pos, reference_build='hg19').id


def range(chr: str, start: int, end: int):
    """Generate all variants within a given genomic range

    Parameters
    ----------
    chr : str
        chromosome
    start : int
        start position
    end : int
        end position
    
    Yields
    ------
    Variant
        a variant from the chosen range
    """
    
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
    """Return a dictionary containing coord: rsid pairs"""
    
    with gzip.open(pydbsnp.VCF_GRCH37, 'rt') as f:
        return dict(generate_coord_rsid_pairs(f))
