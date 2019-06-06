"""
Module for writing bias vector files.
"""

from lib5c.util.system import check_outdir


def write_cis_bias_vector(bias, primermap, outfile, region_order=None):
    """
    Writes a dict of bias vectors to a file.

    Parameters
    ----------
    bias : Dict[str, np.ndarray]
        The keys are region names as strings, the values are the one-dimensional
        bias vector for that region.
    primermap : Dict[str, List[Dict[str, Any]]]
        The primermap or pixelmap that describes the loci whose bias factors are
        contained in the bias vectors.
    outfile : str
        A string reference to a file to write the bias vector to.
    region_order : Optional[List[str]]
        Pass a list of region names as strings to force the regions to be
        written in that order. If this kwarg is not passed, the regions will
        be written in the order of ``primermap.keys()``.
    """
    check_outdir(outfile)
    # deduce regions
    if region_order is None:
        region_order = primermap.keys()

    with open(outfile, 'w') as handle:
        for region in region_order:
            for i in range(len(primermap[region])):
                handle.write('%s\t%s\n' %
                             (primermap[region][i]['name'], bias[region][i]))
