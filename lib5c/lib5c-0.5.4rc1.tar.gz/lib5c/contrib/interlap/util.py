"""
Module containing utilities for interfacing with InterLap objects from the
external ``interlap`` Python package, which provides efficient binary interval
search for finding overlapping genomic features.
"""

from interlap import InterLap


def features_to_interlaps(features, chroms=None):
    """
    Converts feature dicts to InterLap objects.

    Parameters
    ----------
    features : dict of list of dict
        The keys of the outer dict should be chromosome names as strings. The
        values of the outer dict represent lists of features found on that
        chromosome. The inner dicts represent individual genomic features, with
        at least the following keys::

            {
                'chrom': str,
                'start': int,
                'end'  : int
            }

        See ``lib5c.parsers.load_features()`` for more information.
    chroms : list of str, optional
        To create InterLap objects for only specified chromosomes, pass a list
        of their names. Pass None to create InterLap objects for all
        chromosomes.

    Returns
    -------
    dict of InterLap
        The keys are chromosome names as strings, the values are InterLap
        objects containing all features on the chromosome. The original feature
        dicts are saved in the data element of each interval in the InterLap.
    """
    # resolve chroms
    if chroms is None:
        chroms = features.keys()

    return {chrom: InterLap([(f['start'], f['end'] - 1, f)
                             for f in features[chrom]])
            for chrom in chroms}


def query_interlap(interlap, query_feature):
    """
    Searches an InterLap object to find features that overlap a given query
    feature.

    Parameters
    ----------
    interlap : InterLap
        The InterLap object to search. Each interval in the InterLap object must
        have a data element, see
        ``lib5c.contrib.interlap.util.features_to_interlaps()``.
    query_feature : dict
        Dict representing the genomic region in which to search for overlapping
        features. Must have at least the following keys::

            {
                'chrom': str,
                'start': int,
                'end'  : int
            }

    Returns
    -------
    list of dict
        Each dict in the list represents a feature found in the InterLap object
        that overlaps the query feature.
    """
    hits = interlap.find((query_feature['start'], query_feature['end'] - 1))
    return [hit[2] for hit in hits]
