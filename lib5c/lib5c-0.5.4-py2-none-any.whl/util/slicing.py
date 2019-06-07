"""
Module containing utility functions related to matrix and primermap slicing.
"""


def slice_matrix_by_grange(matrix, regional_primermap_x, grange_x,
                           grange_y=None, regional_primermap_y=None):
    """
    Convenience function for slicing matrices.

    Parameters
    ----------
    matrix : np.ndarray
        The matrix to slice.
    regional_primermap_x : list of dict
        The primermap describing the column indices of ``matrix``.
    grange_x : dict
        The genomic range to slice the x-axis of the matrix with (columns).
    grange_y : dict, optional
        The genomic range to slice the y-axis of the matrix with (rows). Pass
        None to assume that the two ranges are equal.
    regional_primermap_y : list of dict, optional
        The primermap describing the row indices of ``matrix``. If ``matrix`` is
        symmetric, pass None.

    Returns
    -------
    np.ndarray, dict, dict
        The np.ndarray is the sliced matrix. The two dicts are the x- and y-axis
        ranges actually represented by the matrix slice.
    """
    if grange_y is None:
        grange_y = grange_x
    if regional_primermap_y is None:
        regional_primermap_y = regional_primermap_x
    slice_x = convert_grange_to_slice(grange_x, regional_primermap_x)
    slice_y = convert_grange_to_slice(grange_y, regional_primermap_y)
    return matrix[slice_y, slice_x], \
        convert_slice_to_grange(slice_x, regional_primermap_x), \
        convert_slice_to_grange(slice_y, regional_primermap_y)


def convert_grange_to_slice(grange, regional_primermap):
    """
    Finds the slice of a regional primermap/pixelmap that covers a given grange.

    Parameters
    ----------
    grange : dict
        The genomic range the slice should cover. Should have keys 'chrom',
        'start', 'end'.
    regional_primermap : list of dict
        The primermap whose indices should make up the slice.

    Returns
    -------
    slice
        The slice.

    Examples
    --------
    >>> regional_primermap = [{'chrom': 'chr1', 'start': 100, 'end': 200},
    ...                       {'chrom': 'chr1', 'start': 300, 'end': 400},
    ...                       {'chrom': 'chr1', 'start': 500, 'end': 600}]
    >>> grange = {'chrom': 'chr1', 'start': 350, 'end': 550}
    >>> convert_grange_to_slice(grange, regional_primermap)
    slice(1, 3, None)
    >>> grange = {'chrom': 'chr1', 'start': 300, 'end': 600}
    >>> convert_grange_to_slice(grange, regional_primermap)
    slice(1, 3, None)
    """
    start = 0
    while regional_primermap[start]['end'] < grange['start']:
        start += 1

    stop = len(regional_primermap) - 1
    while regional_primermap[stop]['start'] > grange['end']:
        stop -= 1

    return slice(start, stop + 1)


def convert_slice_to_grange(s, regional_pixelmap):
    """
    Converts an index-based slice into a dict describing the genomic range
    covered by the slice.

    Parameters
    ----------
    s : slice
        The slice.
    regional_pixelmap : list of dict
        The pixelmap or primermap being indexed into by the slice.

    Returns
    -------
    dict
        The genomic range covered by the slice, as a dict with 'chrom', 'start',
        and 'end' keys.

    Examples
    --------
    >>> regional_pixelmap = [{'chrom': 'chr1', 'start': 100, 'end': 200},
    ...                      {'chrom': 'chr1', 'start': 300, 'end': 400},
    ...                      {'chrom': 'chr1', 'start': 500, 'end': 600}]
    >>> (convert_slice_to_grange(slice(1, 3), regional_pixelmap) ==
    ...  {'chrom': 'chr1', 'start': 300, 'end': 600})
    True
    """
    return {
        'chrom': regional_pixelmap[0]['chrom'],
        'start': regional_pixelmap[s.start]['start'],
        'end': regional_pixelmap[s.stop - 1]['end']
    }
