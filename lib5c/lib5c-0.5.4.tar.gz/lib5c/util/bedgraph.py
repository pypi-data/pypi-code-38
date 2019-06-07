"""
Module containing utilities for manipulating bedgraph files.
"""

from lib5c.parsers.bed import load_features


def reduce_bedgraph(bedfile, pixelmap):
    """
    Reduces a bedgraph file by excluding peaks that fall outside of the regions
    described by a pixelmap.

    Parameters
    ----------
    bedfile : str
        String reference to the bedgraph file to reduce.
    pixelmap : dict of lists of dicts
        The keys of the outer dict are region names. The values are lists, where
        the ``i`` th entry represents the ``i`` th bin in that region. Bins are
        represented as dicts with at least the following structure::

            {
                'chrom': string,
                'start': int,
                'end'  : int
            }

        See ``lib5c.parsers.primers.get_pixelmap()``.

    Returns
    -------
    dict of lists of dicts
        The keys are chromosome names. The values are lists of peaks for that
        chromosome. The peaks are represented as dicts with at least the
        following keys::

            {
                'start': int,
                'end'  : int
            }

    """
    # compute region boundaries
    boundaries = {}
    for region in pixelmap.keys():
        boundaries[region] = {'start': pixelmap[region][0]['start'],
                              'end': pixelmap[region][-1]['end'],
                              'chrom': pixelmap[region][0]['chrom']}

    # parse bedgraph peaks
    peaks = load_features(bedfile, boundaries=[boundaries[region]
                                               for region in pixelmap.keys()])

    return peaks


def in_boundaries(peak, chrom, boundaries):
    """
    Checks to see if a given feature on a given chromosome is within the
    boundaries.

    Parameters
    ----------
    peak : dict
        The feature to check. This dict should have the following structure::

            {
                'start': int,
                'end': int
            }

        See lib5c.parsers.bed.load_features().
    chrom : str
        The chromosome this feature is on.
    boundaries : dict of dicts
        Information about the region boundaries. The outer keys are region names
        as strings. The values are dicts describing the boundaries of that
        region with the following structure::

            {
                'chrom': str,
                'start': int,
                'end': int
            }

    Returns
    -------
    bool
        True if the feature is in one of the regions, False otherwise.
    """
    for region in boundaries:
        if chrom == boundaries[region]['chrom']:
            if (peak['start'] < boundaries[region]['end'] and
                    peak['end'] > boundaries[region]['start']):
                return True
    return False


# test client
def main():
    from lib5c.parsers.primers import get_pixelmap
    bedgraph_features = load_features('test/bedgraph.bed')
    reduced_bedgraph_features = reduce_bedgraph(
        'test/bedgraph.bed', get_pixelmap('test/bins.bed'))
    print(len(bedgraph_features['chr1']))
    print(len(reduced_bedgraph_features['chr1']))
    print(len(bedgraph_features['chr4']))
    print(len(reduced_bedgraph_features['chr4']))
    print(bedgraph_features['chr4'][0])
    print(reduced_bedgraph_features['chr4'][0])


if __name__ == "__main__":
    main()
