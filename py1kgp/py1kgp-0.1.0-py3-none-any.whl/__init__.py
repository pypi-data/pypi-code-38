"""Extract a line from 1KGP data and create an object

A mini-module built to provide an easy interface with 1KGP data in python3.

Examples
-------
import py1kgp
py1kgp.Variant('rs10')
py1kgp.Variant(id='rs10')
py1kgp.Variant(7, 92383888)
py1kgp.Variant(chrom=7, pos=92383888)
py1kgp.fast_genotypes(7, 92383888)
py1kgp.fast_genotypes(7, 92383888, samples='NA21142,NA21143,NA21144')
py1kgp.fast_maf(7, 92383888)
py1kgp.slice_vcf(1, (1000000, 2000000))
py1kgp.slice_vcf(1, (1000000, 2000000), samples='NA21142,NA21143,NA21144')
py1kgp.slice_vcf(1, (1000000, 2000000), samples='AFR')
py1kgp.slice_vcf(1, (1000000, 2000000), samples='samples.panel')
CHR, POS, F = kgp.dicts()

Notes
-----
The Variant class parses an entire 1KGP line into an object, so it might not be
the fastest solution for all cases. This module may be a good place to include
faster utilities, e.g. a function for fast MAF lookup, as the need arises.

Classes
-------
Variant
    a variant
"""

from py1kgp.py1kgp import (
  DIR, Variant, slice_vcf, fast_maf, fast_genotypes, dicts
)
