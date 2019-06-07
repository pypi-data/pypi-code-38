"""
Module for parsing bias vector files.
"""

import numpy as np


def load_bias_vector(bias_file, pixelmap):
    """
    Loads in bias vectors from a bias vector file.

    Parameters
    ----------
    bias_file : str
        String reference to the location of a .bias file to load bias vectors
        from.
    pixelmap : Dict[str, List[Dict[str, Any]]]
        A primermap or pixelmap specifying the information about the regions and
        loci whose bias factors are contained in the ``bias_file``.

    Returns
    -------
    Dict[str, np.ndarray]
        The keys are region names as strings, the values are the one-dimensional
        bias vectors for that region.
    """
    # dict to be returned
    bias_dict = {region: np.zeros(len(pixelmap[region]))
                 for region in pixelmap.keys()}

    # build reverse pixelmap
    reverse_pixelmap = {pixelmap[region][index]['name']: {'region': region,
                                                          'index' : index}
                        for region in pixelmap.keys()
                        for index in range(len(pixelmap[region]))}

    with open(bias_file, 'r') as handle:
        for line in handle:
            # skip comments and blank lines
            if line.startswith('#') or len(line.strip()) == 0:
                continue

            # parse line
            pieces = line.strip().split('\t')
            bin_info = reverse_pixelmap[pieces[0]]
            bias_value = float(pieces[1])

            # store value
            bias_dict[bin_info['region']][bin_info['index']] = bias_value

    return bias_dict
