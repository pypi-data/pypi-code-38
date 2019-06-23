import numpy as np
from mag.py.files import linesplit
def from_delim(file:str, delim:str=',', dtype=None, newline='\n') -> list:
    '''Parses deliminated file into numpy array.

    Args:
    '''
    with open(file, 'r') as f:
        data = np.array([linesplit(line, delim, newline) for line in f])

    if dtype is not None:
        data = data.astype(dtype)
    return data
