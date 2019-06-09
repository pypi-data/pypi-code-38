import numpy as np
import pandas as pd
import scipy


def count(x):
    try:
        return x.count()
    except:
        return len(x)


def missing(x):
    try:
        return (pd.isnull(x)).sum()
    except:
        return (np.isnan(x)).sum()


def mean(x, axis=0):
    try:
        return x.mean(axis=axis, skipna=True)
    except:
        return np.nan


def median(x, axis=0):
    try:
        return x.median(axis=axis, skipna=True)
    except:
        return np.nan


def mode(x):
    return x.mode().iloc[0]


def unique(x, dropna=False):
    return round(
        x.nunique(dropna=dropna) / (count(x) + missing(x) * (dropna == False) * 1) * 100, 2)


def missing(x):
    miss = x.isnull().sum()
    total = x.count()
    return round((miss * 100) / total, 2)


def max(x, axis=0):
    try:
        return x.max()
    except:
        return np.nan


def min(x, axis=0):
    try:
        return x.min()
    except:
        return np.nan


def var(x, axis=0, dof=1):
    try:
        return x.var(axis=axis, ddof=dof)
    except:
        return np.nan


def std(x, axis=0, dof=1):
    try:
        return x.std(axis=axis, ddof=dof)
    except:
        return np.nan


def rng(x, axis=0):
    try:
        return x.max(axis=axis) - x.min(axis=axis)
    except:
        try:
            return max(x) - min(x)
        except:
            return np.nan


def percentile(x, p, axis=0):
    if p > 1: p = p / 100
    try:
        return x.quantile(p, axis=axis)
    except:
        return np.nanpercentile(x, p, axis=axis)


def iqr(x, axis=0):
    try:
        return percentile(x, 0.75, axis=axis) - percentile(x, 0.25, axis=axis)
    except:
        return np.nan


def skew(x, axis=0):
    try:
        return scipy.stats.skew(x, axis=axis, nan_policy='omit')
    except:
        return np.nan


def kurt(x, axis=0):
    try:
        return scipy.stats.kurtosis(x, axis=axis, nan_policy='omit')
    except:
        return np.nan


def top_catg(x, col):
    count = x.groupby(col).size()
    sorted_count = count.sort_values(ascending=False)
    return sorted_count.first_valid_index()


def top_value(x, col):
    count = x.groupby(col).size()
    sorted_count = count.sort_values(ascending=False)
    return sorted_count.iloc[0]
