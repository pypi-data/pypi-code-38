"""statistics.py: 
"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

def histogram( vec, bins = 10, normed = False ):
    """Histogram of given vector.
    """
    a, b = min(vec), max(vec)
    s = (b-a) / float( bins )
    buckets = [ a + s * x for x in range( bins ) ]
    buckets.append( b )

    hist = [ 0 ] * bins
    for i, bb in enumerate( buckets[1:] ):
        aa = buckets[i]
        for x in vec:
            if x >= aa and x <= bb:
                hist[i] += 1

    if normed:
        hist = [ float(x) / len( vec ) for x in hist ]

    return hist, buckets

def test( ):
    import numpy as np
    data = np.random.random( 100 ) * 100
    data = [10,20,30,40,50,60,70,80,90,100]
    print( histogram( data ) )
    print( np.histogram( data ) )

if __name__ == '__main__':
    test()
