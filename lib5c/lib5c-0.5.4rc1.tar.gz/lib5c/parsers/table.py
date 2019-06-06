"""
Module for parsing table files, which function as a simple extension of .counts
files to multiple replicates.
"""

import numpy as np

from lib5c.parsers.util import parse_field
from lib5c.util.table import make_fflj_id_map


def load_table(filename, primermap, sep='\t', dtype=float):
    """
    Loads a table into a counts_superdict structure.

    Parameters
    ----------
    filename : str
        The table file to load.
    primermap : primermap or pixelmap
        Defines the FFLJs or bin-bin pairs.
    sep : str
        The separator used in the table file.
    dtype : numpy-compatible dtype
        The dtype to use when constructing the arrays in the counts_superdict.

    Returns
    -------
    counts_superdict
        The loaded counts_superdict.
    """
    # prepare fflj_id_map
    fflj_id_map = make_fflj_id_map(primermap)

    with open(filename, 'r') as handle:
        # get replicates from header
        replicates = [part.strip() for part in handle.readline().split(sep)[1:]]

        # initialize counts_superdict
        counts_superdict = {rep: {region: np.zeros((len(primermap[region]),
                                                    len(primermap[region])),
                                                   dtype=dtype)
                                  for region in primermap}
                            for rep in replicates}

        # process remaining lines
        for line in handle:
            pieces = line.strip().split(sep)
            region, i, j = fflj_id_map[pieces[0]]
            for k in range(len(replicates)):
                parsed_value = parse_field(pieces[k + 1])
                counts_superdict[replicates[k]][region][i, j] = parsed_value
                counts_superdict[replicates[k]][region][j, i] = parsed_value

    return counts_superdict
