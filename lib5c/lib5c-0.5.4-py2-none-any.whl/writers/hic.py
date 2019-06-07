"""
Module for writing contact matrices to text files formatted in the style of Rao
et al.'s GEO submission.
"""

from lib5c.util.parallelization import parallelize_regions
from lib5c.util.system import check_outdir


@parallelize_regions
def write_rao_matrix(matrix, resolution, outfile):
    """
    Function for writing matrices to text files formatted in the style of Rao
    et al.'s GEO submission.

    See https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE63525 for more
    details.

    Parameters
    ----------
    matrix : np.ndarray
        The matrix to write to file.
    resolution : int
        The resolution of the matrix, in base pairs.
    outfile : str
        String reference to the file to write to.

    Notes
    -----
    To write matrices for all chromosomes in one call, try:

        write_rao_matrix(counts_dict, 40000, {chrom: 'outdir/%s.matrix' % chrom
                                              for chrom in counts_dict})

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.writers.hic import write_rao_matrix
    >>> from lib5c.parsers.hic import load_range_from_contact_matrix
    >>> matrix = np.arange(16).reshape((4, 4))
    >>> matrix += matrix.T
    >>> write_rao_matrix(matrix, 10000, 'test/rao_matrix_written.matrix')
    >>> grange = {'chrom': 'chr1', 'start': 0, 'end': 40000}
    >>> parsed_matrix, _ = load_range_from_contact_matrix(
    ...     'test/rao_matrix_written.matrix', grange)
    >>> np.all(matrix == parsed_matrix)
    True
    """
    check_outdir(outfile)
    with open(outfile, 'w') as handle:
        for i in range(len(matrix)):
            for j in range(i + 1):
                if matrix[i, j] > 0:
                    handle.write('%i\t%i\t%s\n' % (i * resolution,
                                                   j * resolution,
                                                   matrix[i, j]))
