#!-*-coding:utf-8-*-
import numpy as np

__all__ = []
__all__ += ["unique","group_hist"]

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
