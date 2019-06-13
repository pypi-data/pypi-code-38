#!-*-coding:utf-8-*-
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "IPAexGothic"


__all__ = ["hist"]

def hist( data , save=False , path=False ):
    """
    """
    y = list( data.values() )
    x = list( data.keys() )
    plt.bar( np.array( range( len( x ) ) ) , y )
    plt.xticks( np.array( range( len( x ) ) ) , x )

    if save and path:
        plt.savefig( path + "/tf_hist.png" )
    else:
        plt.show()
