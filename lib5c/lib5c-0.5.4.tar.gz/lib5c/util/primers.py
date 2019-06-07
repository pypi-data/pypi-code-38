"""
Module containing utilities for manipulating 5C primer information.
"""

import re


_nsre = re.compile('([0-9]+)')


def natural_sort_key(s):
    """
    Function to enable natural sorting of alphanumeric strings.

    Parameters
    ----------
    s : str
        String being sorted.

    Returns
    -------
    List[Union[int, str]]
        This list is an alternative represenation of the input string that will
        sort in natural order.

    Notes
    -----
    Function written by SO user http://stackoverflow.com/users/15055/claudiu and
    provided in answer http://stackoverflow.com/a/16090640.
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


def determine_region_order(primermap):
    """
    Orders regions in a primermap by genomic coordinate.

    Parameters
    ----------
    primermap : Dict[str, List[Dict[str, Any]]]
        Primermap containing information about the regions to be ordered. See
        ``lib5c.parsers.primers.get_primermap()``.

    Returns
    -------
    List[str]
        List of ordered region names.
    """
    regions = primermap.keys()
    regions.sort(key=lambda x: primermap[x][0]['start'])
    regions.sort(key=lambda x: natural_sort_key(primermap[x][0]['chrom']))
    return regions


def aggregate_primermap(primermap, region_order=None):
    """
    Aggregates a primermap into a single list.

    Parameters
    ----------
    primermap : Dict[str, List[Dict[str, Any]]]
        Primermap to aggregate. See ``lib5c.parsers.primers.get_primermap()``.
    region_order : Optional[List[str]]
        Order in which regions should be concatenated. If None, the regions will
        be concatenated in order of increasing genomic coordinate. See
        ``lib5c.util.primers.determine_region_order()``.

    Returns
    -------
    List[Dict[str, Any]]
        The dicts represent primers in the same format as the inner dicts of the
        passed primermap; however, they exist as a single flat list instead of
        within an outer dict structure. The regions are arranged within this
        list in contiguous blocks, arranged in the order specified by the
        region_order kwarg.

    Notes
    -----
    This function returns a list of references to the original primermap, under
    the assumption that primer dicts are rarely modified. To avoid this, pass a
    copy of the primermap instead of the original primermap.
    """
    # determine region order if not specified
    if region_order is None:
        region_order = determine_region_order(primermap)

    return [primer_dict
            for region in region_order
            for primer_dict in primermap[region]]


def guess_bin_step(regional_pixelmap):
    """
    Guesses the bin step from a regional pixelmap.

    Parameters
    ----------
    regional_pixelmap : List[Dict[str, Any]]
        Ordered list of bins for a single region.

    Returns
    -------
    int
        The guessed bin step for this pixelmap.
    """
    return regional_pixelmap[1]['start'] - regional_pixelmap[0]['start']
