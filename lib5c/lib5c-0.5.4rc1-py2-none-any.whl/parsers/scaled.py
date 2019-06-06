"""
Module for parsing .scaled files.
"""

import numpy as np


def load_scaled(scaledfile):
    """
    Loads the scaled values from a .scaled file into square, symmetric arrays
    and returns them.

    Parameters
    ----------
    scaledfile : str
        String reference to location of .scaled file to load counts from.

    Returns
    -------
    dict of 2d arrays
        The keys are the region names. The values are the arrays of scaled
        values for that region. These arrays are square and symmetric.
    """
    # dict to store scaled values
    scaled = {}

    # parse scaledfile
    with open(scaledfile, 'r') as handle:
        for line in handle:
            # parse region
            region = line.strip('\n').split('\t')[0]

            # add region to dict if this is a new one
            if region not in scaled:
                scaled[region] = []

            # parse value
            value = float(line.strip('\n').split('\t')[1])

            # add this line to the list
            scaled[region].append(value)

    # reshape array
    for region in scaled.keys():
        size = int(np.sqrt(len(scaled[region])))
        scaled[region] = np.asarray(scaled[region]).reshape((size, size))

    return scaled


# test client
def main():
    counts = load_scaled('test/test.scaled')
    print(counts.keys())
    print(len(counts['Klf4']))
    print(len(counts['Klf4'][0]))
    print(counts['Klf4'][0][0])
    print(counts['Klf4'][1][0])
    print(counts['Klf4'][0][1])


if __name__ == "__main__":
    main()
