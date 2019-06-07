"""
Utility functions related to table files.
"""


def make_fflj_id_map(primermap):
    """
    Creates a map from unique FFLJ or bin-bin pair IDs to (region, row, column)
    coordinate tuples.

    Parameters
    ----------
    primermap : primermap or pixelmap
        Defines the fragments or bins that will get IDs assigned.

    Returns
    -------
    Dict[str, Tuple]
        The keys are FFLJ or bin-bin pair IDs as strings. The values are
        (region, row, column) coordinate tuples.
    """
    fflj_id_map = {}
    for region in primermap:
        for i in range(len(primermap[region])):
            for j in range(i + 1):
                fflj_id = '%s_%s' % (primermap[region][j]['name'],
                                     primermap[region][i]['name'])
                coords = (region, i, j)
                fflj_id_map[fflj_id] = coords
    return fflj_id_map
