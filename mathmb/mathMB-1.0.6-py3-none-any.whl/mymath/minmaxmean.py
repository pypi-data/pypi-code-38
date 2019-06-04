import numpy as np

def minmaxmean(x):
    '''Wrapper to print np.min(), np.max(), np.mean() at once'''
    return np.min(x), np.max(x), np.mean(x)
