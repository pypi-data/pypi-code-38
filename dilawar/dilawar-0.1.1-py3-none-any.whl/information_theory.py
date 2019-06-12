"""information_theory.py: 

Functions related to information theory.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import math


def entropy( P ):
    h = 0.0
    for p in P:
        assert p >= 0, 'All values must be positive'
        if p == 0:
            continue
        h -= p * math.log( p, 2 )
    return h


def kl_distance( P, Q ):
    dist = 0.0
    for p, q in zip( P, Q ):
        assert q > 0, 'Q must not have zero entry'
        if p == 0:
            continue 
        dist += (p  * math.log( p/q, 2 ))
    return dist
