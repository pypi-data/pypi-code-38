import numpy as np

def binarize(data:list, cutoff:float=0.5) -> list:
    '''Converts all values of data to either 1 or 0 depending on
    whether or not the value is greater than cutoff.

    Args:
        data (ndarray): an arbitrary array of numerical values
        cutoff (float): a value bounded [0, 1] determining which values are
            converted to one.

    Returns:
        binary_data (ndarray:int): an array with same dimensions as data where
            all values are either 0 or 1
    '''
    return (data > cutoff).astype(int)

def consecutive(data:list, stepsize:float=1) -> list:
    '''Splits data into subarrays where the values in each array vary by stepsize

    Args:
        data (ndarray): a one dimensional array of sorted values
        stepsize (float): a numeric value specifying how close values should be
            to be considered consecutive
    Returns:
        consecutive_numbers (ndarray): a list of values from data where each
            sublist contains values that are exactly stepsize apart
    '''
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)

from mag.py.math import domain
def runs(array:list) -> list:
    '''Returns the [start, stop] values of consectuive numbers in the given array

    Args:
        array (list): a list of values, sorted least to greatest

    Returns:
        runs (list): a list of all runs found in the array, where a run specifies
            the lower and upper bounds of the run
    '''
    return [domain(run) if run.size > 0 else [] for run in consecutive(array)]


def nonzero_1d(data:list) -> list:
    '''Returns the indices of nonzero values in an one-dimensional array.

    Args:
        data (ndarray): an array with one dimension

    Returns:
        indices (ndarray): a one dimensional array containing indicies of data
            which are nonzero
    '''
    return data.nonzero()[0]
