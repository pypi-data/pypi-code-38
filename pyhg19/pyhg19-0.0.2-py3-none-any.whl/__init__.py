"""Get the coordinates of a variant from its RSID, or an RSID from its
coordinates

Examples
--------
rs10_coord = coord('rs10')
print(f'rs10 is on chromosome {rs10_coord.chr} at position {rs10_coord.pos}')

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

Notes
-----
coord() returns an object, which is useful for writing readable code. 

coord_tuple() returns a tuple, which is more lightweight and useful for going
fast.

rsid() returns an RSID (a string).

Classes
-------
Coordinates
    The coordinates of a variant

Functions
---------
coord
    get the coordinates and return them as an object
coord_tuple
    get the coordinates and return them as a tuple
rsid
    get the rsid and return it as a string

Global
------
PATH
    absolute path to the hg19 reference genome
MASKED
    absolute path to the masked hg19 reference genome
BOWTIE2_INDEX
    prefix for a bowtie2 index of the hg19 reference genome
"""

from pyhg19.pyhg19 import coord, coord_tuple, rsid, range, coord_rsid_dict
