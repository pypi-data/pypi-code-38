"""
Module for computing sets of evenly-spaced bins for tiling 5C regions.
"""

from lib5c.util.bed import get_midpoint
from lib5c.util.parallelization import parallelize_regions


def default_bin_namer(bin_index, region_name=None):
    """
    Names a bin given its index and, optionally, the name of the region.

    Parameters
    ----------
    bin_index : int
        The index of this bin, within the region if appropriate.
    region_name : Optional[str]
        The name of the region this bin is in.

    Returns
    -------
    str
        The name for this bin.

    Examples
    --------
    >>> default_bin_namer(3)
    'BIN_003'
    >>> default_bin_namer(123, region_name='Sox2')
    'Sox2_BIN_123'
    """
    if region_name is not None:
        return '%s_BIN_%03d' % (region_name, bin_index)
    return 'BIN_%03d' % bin_index


@parallelize_regions
def determine_regional_bins(regional_primermap, bin_width, region_name=None,
                            bin_namer=default_bin_namer, bin_namer_kwargs=None,
                            region_span='mid-to-mid', bin_number='n'):
    """
    Determines a set of bins of a specified width that will tile a set of
    primers within a region.

    Parameters
    ----------
    regional_primermap : List[Dict[str, Any]]
        An ordered list of fragments in this region. The elements of the list
        are dicts (representing fragments) with at least the following
        structure::

            {
                'chrom': str
                'start': int,
                'end': int
            }

        See ``lib5c.parsers.primers.get_primermap()``.
    bin_width : int
        The width of the bins, in bp.
    region_name : Optional[str]
        The name of the region as a string. If this value is provided, it will
        also be passed on to the bin_namer as a kwarg.
    bin_namer : Callable[[int, ...], str]
        A function mapping bin indices to bin names. This function will be used
        to name the resulting bins. If region_name is passed, it will be passed
        on to this function as a kwarg.
    bin_namer_kwargs : Optional[Dict[Any, Any]]
        Additional kwargs to be passed to the ``bin_namer``.
    region_span : Optional[str]
        Describes whether the span of the region is considered to be stretching
        from the midpoint of the first fragment to the midpoint of the last
        fragment ('mid-to-mid') or from the beginning of the first fragment to
        the end of the last fragment ('start-to-end').
    bin_number : Optional[str]
        Describes how many bins to fit in the region, given that 'n' is the
        largest number of full bins that will fit in the region. Use 'n' to
        reproduce traditional pipeline output, at the risk of leaving some
        fragment midpoints outside of the range of the bins. Use 'n+1' for a
        more conservative binning strategy that is guaranteed to not leave any
        fragment midpoints outside of the region if region_span is 'mid-to-mid'.

    Returns
    -------
    List[Dict[str, Any]]
        An ordered list of bins tiling the region. The elements of the list are
        dicts (representing bins) with the following structure::

            {
                'name': str,
                'chrom': str,
                'start': int,
                'end': int,
                'index': int,
                'region': str (present only if region_name was passed)
            }

    Examples
    --------
    >>> # single fragment results in single bin centered on the fragment
    >>> regional_primermap = [{'chrom': 'chr1', 'start': 2000, 'end': 4000}]
    >>> (determine_regional_bins(regional_primermap, 4000,
    ...                          region_name='Sox2') ==
    ... [{'name': 'Sox2_BIN_000', 'chrom': 'chr1', 'start': 1000, 'end': 5000,
    ...   'index': 0, 'region': 'Sox2'}])
    True

    >>> # examples for region_span='mid-to-mid'
    >>> regional_primermap = [{'chrom': 'chr1', 'start': 2000, 'end': 4000},
    ...                       {'chrom': 'chr1', 'start': 9500, 'end': 10500}]
    >>> (determine_regional_bins(regional_primermap, 5000) ==
    ... [{'name': 'BIN_000', 'chrom': 'chr1', 'start': 4000, 'end': 9000,
    ...   'index': 0}])
    True
    >>> (determine_regional_bins(regional_primermap, 3000) ==
    ... [{'name': 'BIN_000', 'chrom': 'chr1', 'start': 3500, 'end': 6500,
    ...   'index': 0},
    ...  {'name': 'BIN_001', 'chrom': 'chr1', 'start': 6500, 'end': 9500,
    ...   'index': 1}])
    True
    >>> (determine_regional_bins(regional_primermap, 3000,
    ...                          bin_number='n+1') ==
    ... [{'name': 'BIN_000', 'chrom': 'chr1', 'start': 2000, 'end': 5000,
    ...   'index': 0},
    ...  {'name': 'BIN_001', 'chrom': 'chr1', 'start': 5000, 'end': 8000,
    ...   'index': 1},
    ...  {'name': 'BIN_002', 'chrom': 'chr1', 'start': 8000, 'end': 11000,
    ...   'index': 2}])
    True

    >>> # examples for region_span='start-to-end'
    >>> regional_primermap = [{'chrom': 'chr1', 'start': 2000, 'end': 4000},
    ...                       {'chrom': 'chr1', 'start': 9000, 'end': 10000}]
    >>> (determine_regional_bins(regional_primermap, 5000,
    ...                          region_span='start-to-end') ==
    ... [{'name': 'BIN_000', 'chrom': 'chr1', 'start': 3500, 'end': 8500,
    ...   'index': 0}])
    True
    >>> (determine_regional_bins(regional_primermap, 3000,
    ...                          region_span='start-to-end') ==
    ... [{'name': 'BIN_000', 'chrom': 'chr1', 'start': 3000, 'end': 6000,
    ...   'index': 0},
    ...  {'name': 'BIN_001', 'chrom': 'chr1', 'start': 6000, 'end': 9000,
    ...   'index': 1}])
    True
    >>> (determine_regional_bins(regional_primermap, 3000,
    ...                          region_span='start-to-end',
    ...                          bin_number='n+1') ==
    ... [{'name': 'BIN_000', 'chrom': 'chr1', 'start': 1500, 'end': 4500,
    ...   'index': 0},
    ...  {'name': 'BIN_001', 'chrom': 'chr1', 'start': 4500, 'end': 7500,
    ...   'index': 1},
    ...  {'name': 'BIN_002', 'chrom': 'chr1', 'start': 7500, 'end': 10500,
    ...   'index': 2}])
    True
    """
    # resolve bin_namer_kwargs
    if bin_namer_kwargs is None:
        if region_name is None:
            bin_namer_kwargs = {}
        else:
            bin_namer_kwargs = {'region_name': region_name}
    else:
        if region_name is not None:
            bin_namer_kwargs.update({'region_name': region_name})

    # determine chrom for this region
    chrom = regional_primermap[0]['chrom']

    # determine region_start and region_end, honoring region_span
    if region_span == 'start-to-end':
        region_start = regional_primermap[0]['start']
        region_end = regional_primermap[-1]['end']
    elif region_span == 'mid-to-mid':
        region_start = get_midpoint(regional_primermap[0])
        region_end = get_midpoint(regional_primermap[-1])
    else:
        raise NotImplementedError('region_span method %s not implemented'
                                  % region_span)

    # compuite region_size
    region_size = region_end - region_start

    # determine number_of_bins, honoring bin_number
    if bin_number == 'n':
        number_of_bins = max(int(region_size / bin_width), 1)
    elif bin_number == 'n+1':
        number_of_bins = int(region_size / bin_width) + 1
    else:
        raise NotImplementedError('bin_number method %s not implemented'
                                  % bin_number)

    # compute region_midpoint
    region_midpoint = (region_start + region_end) / 2

    # determine bins
    bin_list = [{'name' : bin_namer(i, **bin_namer_kwargs),
                 'chrom': chrom,
                 'start': int(region_midpoint +
                              (i - (number_of_bins / 2.0)) * bin_width),
                 'end'  : int(region_midpoint +
                              (i + 1 - (number_of_bins / 2.0)) * bin_width),
                 'index': i}
                for i in range(number_of_bins)]

    # include region_name if available
    if region_name is not None:
        for i in range(number_of_bins):
            bin_list[i]['region'] = region_name

    return bin_list
