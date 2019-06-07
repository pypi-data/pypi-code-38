"""
Module for writing the results of principle component analyses to disk.
"""

import numpy as np

from lib5c.util.system import check_outdir


def write_pca(outfile, proj, rep_names=None, pve=None):
    """
    Write PCA projections to a csv file.

    Parameters
    ----------
    outfile : str
        String reference to the file to write to.
    proj : np.ndarray
        The PCA projections to plot
    rep_names : Optional[List[str]]
        The replicate names in the order of the rows of ``proj``, to be used to
        write the header line.
    pve : Optional[List[float]]
        The percent variance explained for each component, to be included in the
        footer.
    """
    check_outdir(outfile)
    header = ','.join([rep for rep in rep_names]) if rep_names else None
    footer = '' if pve is None else '\nPVE:,'+','.join([str(p) for p in pve])
    np.savetxt(outfile, proj.T, delimiter=',', comments='', header=header,
               footer=footer)
