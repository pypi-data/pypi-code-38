"""
Module for parsing .counts files.
"""

from math import sqrt

import numpy as np

from lib5c.parsers.primer_names import default_primer_parser, default_bin_parser
from lib5c.util.primers import determine_region_order, aggregate_primermap
from lib5c.parsers.util import parse_field


def set_nans(counts, primermap):
    """
    Sets nan's in counts dict for ligations considered impossible according to a
    primermap with strand information.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The keys are the region names. The values are the arrays of counts
        values for that region. These arrays are square and symmetric.
    primermap : Dict[str, List[Dict[str, Any]]]
        The keys of the outer dict are region names. The values are lists, where
        the :math:`i` th entry represents the :math:`i` th primer in that
        region. Primers are represented as dicts with the following structure::

            {
                'chrom'  : str,
                'start'  : int,
                'end'    : int,
                'strand' : '+' or '-'
            }

        See ``lib5c.parsers.primers.get_primermap()``.

    Notes
    -----
    If the primermap passed has no strand information, this function will do
    nothing.

    This function operates in-place.
    """
    for region in counts.keys():
        for i in range(len(primermap[region])):
            for j in range(i+1):
                if ('strand' in primermap[region][i].keys() and
                        'strand' in primermap[region][j].keys()):
                    if primermap[region][i]['strand'] == \
                            primermap[region][j]['strand']:
                        counts[region][i, j] = np.nan
                        counts[region][j, i] = np.nan


def set_cis_trans_nans(counts, aggregated_primermap):
    """
    Sets nan's in a complete cis and trans counts matrix for ligations
    considered impossible according to a primermap with strand information.

    Parameters
    ----------
    counts : np.ndarray
        Square, symmetric array storing the complete cis and trans counts, with
        the regions arranged as implied by the ``aggregated_primermap``
    aggregated_primermap : List[Dict[str, Any]]
        The dicts in the lists represent primers, equal in number and order to
        the side length of the counts matrix, and have the following structure::

            {
                'chrom'  : str,
                'start'  : int,
                'end'    : int,
                'strand' : '+' or '-'
            }

        See ``lib5c.parsers.primers.get_primermap()`` and
        ``lib5c.util.primers.aggregate_primermap()``.

    Notes
    -----
    If the aggregated primermap passed has no strand information, this function
    will do nothing.

    This function operates in-place.
    """
    for i in range(len(aggregated_primermap)):
        for j in range(i+1):
            if ('strand' in aggregated_primermap[i].keys() and
                    'strand' in aggregated_primermap[j].keys()):
                if aggregated_primermap[i]['strand'] == \
                        aggregated_primermap[j]['strand']:
                    counts[i, j] = np.nan
                    counts[j, i] = np.nan


def load_cis_trans_counts(countsfile, primermap,
                          name_parser=default_primer_parser, force_nan='always',
                          region_order=None):
    """
    Loads the counts values from a primer-primer pair .counts file into a single
    square, symmetric array, and returns it.

    Parameters
    ----------
    countsfile : str
        String reference to location of .counts file to load counts from.
    primermap : Dict[str, List[Dict[str, Any]]]
        The keys of the outer dict are region names. The values are lists, where
        the :math:`i` th entry represents the :math:`i` th primer in that
        region. Primers are represented as dicts with the following structure::

            {
                'chrom' : str,
                'start' : int,
                'end'   : int
            }

        See ``lib5c.parsers.primers.get_primermap()``.
    name_parser : Optional[Callable[[str], Dict[str, Any]]]
        Function that takes in the primer names in the countsfile and returns a
        dict containing key-value pairs containing information required to
        identify the primer. At a minimum, this dict must have the following
        structure::

            {
                'region': str
            }

        This information is necessary to deduce what region a given primer in
        the countsfile belongs to.
    force_nan : Optional[str]
        If 'always' is passed and if the primermap contains strand information,
        impossible ligations will be always set to nan. If 'implicit' is passed,
        impossible ligations will be set to nan when implied by the strand
        information in the primermap, but not when the ligations are explicitly
        present in the countsfile. If 'never' is passed, strand information will
        be ignored and impossible ligations will not be identified.
    region_order : Optional[List[str]]
        If passed, this list will be used to determine the order in which the
        regions will be concatenated in. If not passed, the regions will be
        concatenated in order of genomic coordinate.

    Returns
    -------
    np.ndarray
        The square, symmetric array of counts.
    """
    # determine region order if not specified
    if region_order is None:
        region_order = determine_region_order(primermap)

    # aggregate primermap
    aggregated_primermap = aggregate_primermap(primermap, region_order)

    # create reverse lookup table for aggregated primermap
    reverse_aggregated_primermap = {aggregated_primermap[i]['name']: i
                                    for i in range(len(aggregated_primermap))}

    # initialize counts array
    counts = np.zeros([len(aggregated_primermap), len(aggregated_primermap)])

    # set nan's for 'implicit' mode
    if force_nan == 'implicit':
        set_cis_trans_nans(counts, aggregated_primermap)

    # parse countsfile
    with open(countsfile, 'r') as handle:
        for line in handle:
            # skip comments
            if line.startswith('#'):
                continue

            # parse line information
            name1 = line.strip().split('\t')[0]
            name2 = line.strip().split('\t')[1]
            value = float(line.strip().split('\t')[2])

            region1 = name_parser(name1)['region']
            region2 = name_parser(name1)['region']

            # skip unrecognized regions
            if (region1 not in primermap.keys() or
                    region2 not in primermap.keys()):
                continue

            # identify indices within aggregated primermap
            index1 = None
            if name1 in reverse_aggregated_primermap:
                index1 = reverse_aggregated_primermap[name1]
            index2 = None
            if name2 in reverse_aggregated_primermap:
                index2 = reverse_aggregated_primermap[name2]

            # skip unrecognized primers
            if index1 is None or index2 is None:
                continue

            # record value
            counts[index1, index2] = value
            counts[index2, index1] = value

    # set nan's for 'always' mode
    if force_nan == 'always':
        set_cis_trans_nans(counts, aggregated_primermap)

    return counts


def load_counts(countsfile, primermap, force_nan='always', dtype=float):
    """
    Loads the counts values from a primer-primer pair .counts file into square,
    symmetric arrays and returns them.

    Parameters
    ----------
    countsfile : str
        String reference to location of .counts file to load counts from.
    primermap : Dict[str, List[Dict[str, Any]]]
        The keys of the outer dict are region names. The values are lists, where
        the :math:`i` th entry represents the :math:`i` th primer in that
        region. Primers are represented as dicts with the following structure::

            {
                'chrom' : str,
                'start' : int,
                'end'   : int
            }

        See ``lib5c.parsers.primers.load_primermap()``.
    force_nan : Optional[str]
        If 'always' is passed and if the primermap contains strand information,
        impossible ligations will be always set to nan. If 'implicit' is passed,
        impossible ligations will be set to nan when implied by the strand
        information in the primermap, but not when the ligations are explicitly
        present in the countsfile. If 'never' is passed, strand information will
        be ignored and impossible ligations will not be identified.
    dtype : {int, float}
        Sets the dtype for the matrix. If the value column contains strings this
        will be ignored and the dtype will be set to '\|S25'.

    Returns
    -------
    Dict[str, np.ndarray]
        The keys are the region names. The values are the arrays of counts
        values for that region. These arrays are square and symmetric.
    """
    try:
        counts = dict(np.load(countsfile))
        try:
            for region in counts:
                np.testing.assert_allclose(counts[region], counts[region].T,
                                           equal_nan=True)
        except AssertionError:
            raise AssertionError('input .npz contains non-symmetric matrices')
    except (IOError, ValueError):
        # half-hearted dtype inference for strings
        value_cast_fn = dtype
        with open(countsfile, 'r') as handle:
            for line in handle:
                if line.startswith('#'):
                    continue
                field_value = parse_field(line.split('\t')[2])
                if field_value == np.nan:
                    continue
                if type(field_value) == str:
                    def value_cast_fn(x):
                        return str(x).strip()
                    dtype = '|S25'
                break

        # initialize counts arrays
        counts = {}
        for region in primermap.keys():
            counts[region] = np.zeros([len(primermap[region]),
                                       len(primermap[region])], dtype=dtype)

        # set nan's for 'implicit' mode
        if force_nan == 'implicit':
            set_nans(counts, primermap)

        # create reverse lookup table
        reverse_map = {primermap[region][index]['name']: (region, index)
                       for region in primermap.keys()
                       for index in range(len(primermap[region]))}

        # parse countsfile
        with open(countsfile, 'r') as handle:
            for line in handle:
                # skip comments
                if line.startswith('#'):
                    continue

                # parse line information
                name1 = line.strip().split('\t')[0]
                name2 = line.strip().split('\t')[1]
                value = value_cast_fn(line.strip('\n ').split('\t')[2])

                # skip unrecognized primers
                if name1 not in reverse_map or name2 not in reverse_map:
                    continue

                # identify indices within region
                region1, index1 = reverse_map[name1]
                region2, index2 = reverse_map[name2]

                # skip trans interactions
                if not region1 == region2:
                    continue

                # record value
                counts[region1][index1, index2] = value
                counts[region1][index2, index1] = value

    # set nan's for 'always' mode
    if force_nan == 'always':
        set_nans(counts, primermap)

    return counts


def load_counts_legacy(countsfile, name_parser=default_bin_parser,
                       pixelmap=None):
    """
    Loads the counts values from a binned .counts file into square, symmetric
    arrays and returns them.

    Parameters
    ----------
    countsfile : str
        String reference to location of .counts file to load counts from.
    name_parser : Optional[Callable[[str], Dict[str, Any]]]
        Function that takes in the bin name column of the countsfile and returns
        a dict containing key-value pairs containing information required to
        identify the bin. At a minimum, this dict must have the following
        structure::

            {
                'region': str,
                'index': int
            }

        This information is necessary to deduce what region a given bin in the
        countsfile belongs to. The index key is optional, but recommended. If
        present, its value should be the zero-based index of the bin within the
        region. If not present, the pixelmap will be searched to identify the
        bin index.
    pixelmap : Optional[Dict[str, List[Dict[str, Any]]]]
        The keys of the outer dict are region names. The values are lists, where
        the :math:`i` th entry represents the :math:`i` th bin in that region.
        Bins are represented as dicts with the following structure::

            {
                'chrom': str,
                'start': int,
                'end'  : int,
                'name' : str
            }

        See ``lib5c.parsers.get_pixelmap()``. The pixelmap is used to identify
        the index of a bin within a region. If ``name_parser`` returns an index
        key, you can pass ``None`` here since the index will be determined from
        the bin name.

    Returns
    -------
    Dict[str, np.ndarray]
        The keys are the region names. The values are the arrays of counts
        values for that region. These arrays are square and symmetric.

    Notes
    -----
    This function casts the counts values in the countsfile to floats, so it
    will work even if the countsfile actually contains pseudocounts or other
    non-integer values.
    """

    # dict to store the unshaped count information
    unshaped_counts = {}

    # parse countsfile
    with open(countsfile, 'r') as handle:
        for line in handle:
            # split line on tab
            pieces = line.strip().split('\t')

            # parse bin names
            name1_fields = name_parser(pieces[0])
            name2_fields = name_parser(pieces[1])

            # deduce region
            region = name1_fields['region']

            # deduce bin1 index
            bin1 = None
            # easy way: use index returned by name_parser
            if 'index' in name1_fields.keys():
                bin1 = name1_fields['index']
            # hard way: search pixelmap for bin with this name
            else:
                for i in range(len(pixelmap[region])):
                    if pixelmap[region][i]['name'] == pieces[0]:
                        bin1 = i

            # deduce bin2 index
            bin2 = None
            # easy way: use index returned by name_parser
            if 'index' in name2_fields.keys():
                bin2 = name2_fields['index']
            # hard way: search pixelmap for bin with this name
            else:
                for i in range(len(pixelmap[region])):
                    if pixelmap[region][i]['name'] == pieces[1]:
                        bin2 = i

            # parse value
            value = float(pieces[2])

            # add region to dict if this is a new one
            if region not in unshaped_counts:
                unshaped_counts[region] = []

            # add this line to the list
            unshaped_counts[region].append({'bin1' : bin1,
                                            'bin2' : bin2,
                                            'value': value})

    # dict to store 2D arrays
    counts = {}

    for region in unshaped_counts:
        # determine the size of the 2D array we should create for this region
        # this should be the inverse function of (n**2 - n)/2 + n
        size = int(0.5 * (-1 + sqrt(8*len(unshaped_counts[region]) + 1)))

        # initialize this new 2D array
        counts[region] = np.zeros([size, size])

        # fill in this array
        for unshaped_count in unshaped_counts[region]:
            counts[region][unshaped_count['bin1'], unshaped_count['bin2']] = \
                unshaped_count['value']
            counts[region][unshaped_count['bin2'], unshaped_count['bin1']] = \
                unshaped_count['value']

    return counts


def load_counts_by_name(countsfile, name_list=None, primermap=None,
                        locusmap=None, force_nan='always', region_order=None):
    """
    Loads the counts values from any .counts file into a single square,
    symmetric array, and returns it.

    Parameters
    ----------
    countsfile : str
        String reference to location of .counts file to load counts from.
    name_list : Optional[List[str]]
        Ordered list of locus names as strings.
    primermap : Optional[Dict[str, List[Dict[str, Any]]]]
        The keys of the outer dict are region names. The values are lists, where
        the ith entry represents the ith primer in that region. Primers are
        represented as dicts with the following structure::

            {
                'chrom' : str,
                'start' : int,
                'end'   : int
            }

        See lib5c.parsers.primers.get_primermap().
    locusmap : Optional[LocusMap]
        Locus information as a LocusMap object.
    force_nan : Optional[str]
        If 'always' is passed and if the primermap contains strand information,
        impossible ligations will be always set to nan. If 'implicit' is passed,
        impossible ligations will be set to nan when implied by the strand
        information in the primermap, but not when the ligations are explicitly
        present in the countsfile. If 'never' is passed, strand information will
        be ignored and impossible ligations will not be identified.
    region_order : Optional[List[str]]
        If passed, this list will be used to determine the order in which the
        regions will be concatenated in. If not passed, the regions will be
        concatenated in order of genomic coordinate. If name_list is passed,
        this kwarg is ignored.

    Returns
    -------
    np.ndarray
        The square, symmetric array of counts.
    """
    # determine region order if not specified
    if not name_list and region_order is None:
        if primermap:
            region_order = determine_region_order(primermap)
        elif locusmap:
            region_order = locusmap.get_regions()

    # aggregate primermap
    aggregated_primermap = None
    if primermap:
        aggregated_primermap = aggregate_primermap(primermap, region_order)

    # create reverse lookup table
    if primermap:
        reverse_map = {aggregated_primermap[i]['name']: i
                       for i in range(len(aggregated_primermap))}
    elif name_list:
        reverse_map = {name_list[index]: index
                       for index in range(len(name_list))}
    elif locusmap:
        reverse_map = {locusmap.locus_list[index].get_name(): index
                       for index in range(locusmap.size())}

    # deduce size
    if primermap:
        size = len(aggregated_primermap)
    elif name_list:
        size = len(name_list)
    elif locusmap:
        size = locusmap.size()
    else:
        raise ValueError('could not determine size of matrix')

    # initialize counts array
    counts = np.zeros([size, size])

    # set nan's for 'implicit' mode
    if force_nan == 'implicit':
        if primermap:
            set_cis_trans_nans(counts, aggregated_primermap)
        elif locusmap:
            set_cis_trans_nans(counts, locusmap.as_list_of_dict())

    # parse countsfile
    with open(countsfile, 'r') as handle:
        for line in handle:
            # skip comments
            if line.startswith('#'):
                continue

            # parse line information
            name1 = line.strip().split('\t')[0]
            name2 = line.strip().split('\t')[1]
            value = float(line.strip().split('\t')[2])

            # identify indices within aggregated primermap
            index1 = None
            if name1 in reverse_map:
                index1 = reverse_map[name1]
            index2 = None
            if name2 in reverse_map:
                index2 = reverse_map[name2]

            # skip unrecognized primers
            if index1 is None or index2 is None:
                continue

            # record value
            counts[index1, index2] = value
            counts[index2, index1] = value

    # set nan's for 'always' mode
    if force_nan == 'always':
        if primermap:
            set_cis_trans_nans(counts, aggregated_primermap)
        elif locusmap:
            set_cis_trans_nans(counts, locusmap.as_list_of_dict())

    return counts


# test client
def main():
    from lib5c.parsers.primers import load_primermap
    pixelmap = load_primermap('test/bins.bed')
    counts = load_counts('test/test.counts', pixelmap)
    print(counts.keys())
    print(len(counts['Klf4']))
    print(len(counts['Klf4'][0]))
    print(counts['Klf4'][0][0])
    print(counts['Klf4'][1][0])
    print(counts['Klf4'][0][1])

    counts = load_counts('test/peaks.counts', pixelmap)
    print(counts.keys())
    print(len(counts['Klf4']))
    print(len(counts['Klf4'][0]))
    print(counts['Klf4'][0][0])
    print(counts['Klf4'][1][0])
    print(counts['Klf4'][0][1])

    primermap = load_primermap('test/primers.bed')
    counts = load_counts('test/test_raw.counts', primermap)
    print(len(counts['Klf4']))
    print(len(counts['Klf4'][0]))
    print(counts['Klf4'][75][75])
    print(counts['Klf4'][75][142])
    print(counts['Klf4'][142][75])


if __name__ == "__main__":
    main()
