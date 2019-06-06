"""
Module for writing table files.
"""

from lib5c.util.table import make_fflj_id_map
from lib5c.util.system import check_outdir


def write_table(filename, counts_superdict, primermap, sep='\t'):
    """
    Writes a counts_superdict structure as a single table file.

    Parameters
    ----------
    filename: str
        The filename to write to.
    counts_superdict : counts_superdict
        The counts_superdict to write.
    primermap : primermap or pixelmap
        Defines the FFLJs or bin-bin pairs.
    sep : str
        The separator to use when writing the table file.
    """
    check_outdir(filename)
    fflj_id_map = make_fflj_id_map(primermap)
    replicates = counts_superdict.keys()
    with open(filename, 'w') as handle:
        handle.write(sep.join(['fflj_id'] + replicates) + '\n')
        for fflj_id in fflj_id_map:
            region, i, j = fflj_id_map[fflj_id]
            handle.write(sep.join([fflj_id]
                                  + [str(counts_superdict[rep][region][i, j])
                                     for rep in replicates]) + '\n')
