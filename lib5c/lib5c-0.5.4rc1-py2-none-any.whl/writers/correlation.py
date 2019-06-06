"""
Module for writing pairwise correlation matrices to text files.
"""

from lib5c.util.system import check_outdir


def write_correlation_table(correlation_matrix, outfile, labels=None, sep=','):
    """
    Write a pairwise correlation matrix to a text file.

    Parameters
    ----------
    correlation_matrix : np.ndarray
        The pairwise correlation matrix to write.
    outfile : str
        String reference to the file to write to.
    labels : Optional[List[str]]
        Pass a list of strings equal to the number of rows/columns in the
        ``correlation_matrix`` to label the rows and columns in the output file
        with these labels in the headers.
    sep : str
        The separator to use to separate columns in the written text file.
    """
    check_outdir(outfile)
    with open(outfile, 'w') as handle:
        if labels:
            for label in labels:
                handle.write('%s%s' % (sep, label))
        handle.write('\n')
        for i in range(len(correlation_matrix)):
            if labels:
                handle.write(labels[i])
            for j in range(len(correlation_matrix)):
                handle.write('%s%s' % (sep, correlation_matrix[i, j]))
            handle.write('\n')
