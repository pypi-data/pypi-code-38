import numpy as np
def from_delim(file:str, delim:str=',', dtype=None, newline='\n') -> list:
    with open(file, 'r') as f:
        data = np.array([line.rstrip(newline).split(delim) for line in f])

    if dtype is not None:
        data = data.astype(dtype)
    return data
