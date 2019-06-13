#!-*-coding:utf-8-*-
import pandas as pd

__all__ = []
__all__ += ["csv"]

def csv( file ):
    """
    CSV Loader
    """

    return pd.read_csv(file)
