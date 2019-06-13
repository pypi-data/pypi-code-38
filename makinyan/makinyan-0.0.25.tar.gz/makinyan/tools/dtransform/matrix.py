#!-*-coding:utf-8-*-
import sys
import pandas as pd
import numpy as np

__all__ = []
__all__ += ["unique","group_hist","df_trans"]

def unique( mat ):
    """
    Get unique mat
    """
    return np.unique( mat )


def group_hist( mat ):
    """
    Get histgram in matrix
    """
    hist = {}
    matrix = unique( mat )
    if np.array( mat ).ndim >= 2:
        for unq in matrix:
            hist[unq] = 0
            for m in mat:
                hist[unq] += m.count(unq)
    else:
        for unq in matrix:
            hist[unq] = mat.count( unq )

    return hist


def df_trans( tap=() , labels=[] ):
    """
    Create DataFrame
    """
    dic = {}
    count = 0
    for lab in labels:
        dic[ lab ] = tap[ count ]

        count += 1

    df = pd.DataFrame( dic )

    return df
