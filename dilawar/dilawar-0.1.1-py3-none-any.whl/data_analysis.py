"""data_analysis.py: 

Helper function related to data analysis.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2016, Dilawar Singh"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"


import sys
import os
import math
import numpy as np
from collections import defaultdict
import scipy.signal  as _sig

def change_sign( vec ):
    # use np.signbit instead of np.sign
    # this is not the best way to compute the zero-crossing. 
    #
    # For b = [ 1, 2, 0, -1, 0, 0, -1, 2], it returns 3 crossing though there
    # are only 2.
    idx = np.signbit( vec ) != np.signbit( np.roll(vec, 1))
    return np.where( idx )[0][1:]

def isclose( v1, v2, eabs = 1e-3 ):
    return abs( v1 - v2 ) < eabs

def is_periodic_helper( vec ):
    # List of timeperiods. It may contain 1 timeperiod of multiple timeperid.
    # Essentially we are looking of repeating substring.
    tps = vec.copy( )
    res = [ ]
    while sum(tps) > 1:
        x0 = tps[np.nonzero(tps)][0]
        ts = [ i for i, x in enumerate(tps) if isclose(x,x0,max(3,0.1*x0)) ]
        if len(ts) < 2:
            continue
        res.append( (x0, np.mean(np.diff(ts))) )
        tps[ts] = 0

    periods, periodicity = zip( *res )
    if min(periodicity) == max(periodicity):
        return np.sum( periods )
    return 0

def find_period( vec, polar = False, ax = None):
    # normalize the vector
    if polar:
        vec[:,0] = vec[:,0] % (2*np.pi) 
    ref = vec[-1]
    dist = np.zeros( len(vec) )
    phase = np.zeros( len(vec) )
    periods = [ ]
    prevI = 0
    for i, v in enumerate(vec[::-1]):
        dist[i] = sum( (v - ref) ** 2) ** 0.5
        phase[i] = math.atan(v[1]/v[0]) - math.atan(ref[1] / ref[0])

    # normalize distance.
    if dist.max( ) == dist.min():
        return False

    if phase.max() == phase.min():
        return False

    if ax is not None:
        ax.plot( dist ) #, color = 'red' )

    zeroCross = change_sign( phase )
    valsAtZero = dist[zeroCross]

    # remove zero-crossings where distance is not close to zero.
    goodPoints = [ x for x in zip(zeroCross, valsAtZero) if not isclose(x[1],0) ]
    if len( goodPoints) < 1:
        return False

    zeroCross, valsAtZero = zip(*goodPoints)
    if len(zeroCross) == 0:
        return 0

    timePeriod = np.diff( zeroCross )
    return is_periodic_helper( timePeriod )


def smooth( sig, N = 100 ):
    window = np.ones( N ) / float( N )
    return np.convolve(  sig, window, 'same' )

def digitize( sig, levels, thres = 4 ):
    for x in levels:
        sig[ (sig > (x-thres)) & (sig < (x+thres)) ] = x
    sig[ np.isnan( sig ) ] = 0
    return sig 

def find_transitions( vec, levels, thres = 4 ):
    sig = digitize( vec, levels, thres )
    result = defaultdict( list )
    for x in levels:
        xIds = np.where( vec ==  x )[0]
        result[ 'kramer_time' ].append( (x, len( xIds ) / 1.0 / len( vec )) )

    trans = np.diff( sig ) 

    result[ 'up_transitions' ] = np.where( trans > 0 )[0]
    result[ 'down_transitions' ] = np.where( trans < 0 )[0]

    return result, sig

def test( datafile ):
    import matplotlib.pyplot as plt
    import pandas as pd
    data = pd.read_csv( datafile, sep = ' ', comment = '#' )
    data.dropna( how = 'any' )
    camkii = data.filter( regex = r'x0y\d.+' )
    tvec = data[ 'time' ]
    lowCaMKII = np.sum( camkii, axis = 1 )
    sig = smooth( lowCaMKII, 500 )
    res, newY = find_transitions( sig, [0,8,16] )
    print( res )
    upT = tvec[ res[ 'up_transitions' ] ]
    downT = tvec[ res[ 'down_transitions' ] ]

    plt.subplot( 311 )
    plt.plot( tvec, lowCaMKII  )
    plt.plot( upT, sig.max() * np.ones( len( upT ) ) , '+' )
    plt.plot( downT, sig.min() * np.ones( len( downT ) ) , '+' )
    plt.subplot( 312 )
    #plt.plot( tvec, step_detection( yvec, 0, 8 ) )
    plt.plot( tvec, sig )
    plt.subplot( 313 )
    plt.plot( tvec, newY )
    plt.savefig( '%s_transitions.png' % datafile )

def main( ):
    datafile = sys.argv[1]
    test(datafile)

# Alias. Deprecated
compute_transitions = find_transitions

if __name__ == '__main__':
    main()
