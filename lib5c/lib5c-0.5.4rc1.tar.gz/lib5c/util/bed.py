"""
Module containing utilities for manipulating BED files and BED features.

BED features are commonly represented as dicts with the following structure::

    {
        'chrom': str
        'start': int,
        'end'  : int,
    }

but may also contain additional fields.
"""

import re


GRANGE_PATTERN = re.compile('(\w+):(\d+)-(\d+)')


def count_intersections(query_feature, feature_set):
    """
    Counts the number of times a query feature is hit by a set of other
    features.

    Parameters
    ----------
    query_feature : Dict[str, Any]
        The feature to count intersections for.
    feature_set : List[Dict[str, Any]]
        The set of features to intersect with the query feature.

    Returns
    -------
    int
        The number of intersections

    Notes
    -----
    Features are represented as dicts with the following structure::

            {
                'chrom': str
                'start': int,
                'end'  : int,
            }

    See ``lib5c.parsers.bed.load_features()``.
    """
    counter = 0
    for feature in feature_set:
        if check_intersect(query_feature, feature):
            counter += 1
    return counter


def check_intersect(a, b):
    """
    Checks to see if two features intersect.

    Parameters
    ---------
    a, b : Dict[str, Any]
        The two features to check for intersection.

    Returns
    -------
    bool
        True if the features intersect, False otherwise.

    Notes
    -----
    Features are represented as dicts with the following structure::

            {
                'chrom': str
                'start': int,
                'end'  : int,
            }

    See ``lib5c.parsers.bed.load_features()``.
    """
    if (
        a['chrom'] == b['chrom'] and
        a['end'] > b['start'] and
        b['end'] > a['start']
    ):
        return True
    return False


def flatten_features(features):
    """
    Flattens a features dict and returns a flat list of features.

    Typically, BED features are kept in dicts organized by chromosome. For
    example, this is the data structure returned by
    ``lib5c.parsers.bed.load_features()``. When a flat list is desired, this
    function can be used to flatten the dictionary into a simple list.

    Parameters
    ----------
    features : Dict[str, List[Dict[str, Any]]]
        The keys are chromosome names. The values are lists of features for that
        chromosome. The features are represented as dicts with at least the
        following keys::

            {
                'start': int,
                'end'  : int
            }

    Returns
    -------
    List[Dict[str, Any]]
        These dicts, which represent the same features as those contained in the
        original dict, have the following keys::

            {
                'chrom': str,
                'start': int,
                'end'  : int
            }

        as well as any additional keys that were present in the inner dicts of
        the features dict passed to this function.

    Notes
    -----
    If the dicts that describe the features already contain a 'chrom' key, that
    key's value will get overwritten during the flattening.
    """

    flattened_list = []
    for chrom in features.keys():
        for feature in features[chrom]:
            feature['chrom'] = chrom
        flattened_list.extend(features[chrom])
    return flattened_list


def get_midpoint(fragment, force_int=False):
    """
    Gets the midpoint of a fragment.

    Parameters
    ----------
    fragment : Dict[str, Any]
        The fragment to find the midpoint of. The fragment must be represented
        as a dict with at least the following keys::

            {
                'start': int,
                'end': int
            }
    force_int : bool
        Return an int rounded towards zero instead of a float.

    Returns
    -------
    float
        The midpoint of the fragment, rounded towards zero if force_int is True.

    Examples
    --------
    >>> fragment = {'start': 50, 'end': 100}
    >>> get_midpoint(fragment)
    75.0
    """
    if force_int:
        return int(get_midpoint(fragment))
    return (fragment['start'] + fragment['end']) / 2.0


def get_mid_to_mid_distance(fragment_a, fragment_b):
    """
    Gets the mid-to-mid distance between two fragments.

    Parameters
    ----------
    fragment_a, fragment_b : Dict[str, Any]
        The fragments to find the distance between. The fragments must be
        represented as dicts with at least the following keys::

            {
                'start': int,
                'end': int
            }

    Returns
    -------
    float
        The mid-to-mid distance
    """
    return abs(get_midpoint(fragment_a) - get_midpoint(fragment_b))


def parse_feature_from_string(grange_string):
    """
    Parses BED feature from a string specifying the genomic range.

    Parameters
    ----------
    grange_string : str
        The genomic range to parse, specified as a string of the form
        <chrom>:<start>-<end>. The interval is interpreted as a BED interval
        (0-based index, half-open interval).

    Returns
    -------
    dict
        The BED feature dict, which has keys 'chrom', 'start', and 'end'.
    """
    chrom, start, end = GRANGE_PATTERN.match(grange_string).groups()
    return {'chrom': chrom, 'start': int(start), 'end': int(end)}


# test client
def main():
    from lib5c.parsers.bed import load_features
    # get some features
    features_a = load_features(
        'test/annotations/V65EScells_CTCFMed12Smc1_2015.bed')
    features_b = load_features(
        'test/annotations/V65EScells_Superenhancers_1_2015.bed')

    # test count_intersections
    print(count_intersections(features_b['chr7'][0],
                              flatten_features(features_a)))


if __name__ == "__main__":
    main()
