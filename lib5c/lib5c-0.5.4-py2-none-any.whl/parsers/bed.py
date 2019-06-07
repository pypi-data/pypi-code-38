"""
Module for parsing .bed files.
"""

from lib5c.util.bed import count_intersections


def load_features(bedfile, id_index=None, value_index=None, boundaries=None,
                  strict=True):
    """
    Loads the features from a .bed file into dicts and returns them.

    Parameters
    ----------
    bedfile : str
        String reference to location of .bed file to load features from.
    id_index : int
        If passed, indicates the column index of the id field.
    value_index : int
        If passed, indicates the column index of the value field.
    boundaries : list of dicts
        If passed, features will only be loaded if they intersect at least one
        of the features in this list. The features should be represented as
        dicts with the following structure::

            {
                'chrom': str,
                'start': int,
                'end'  : int
            }

    strict : boolean
        If True, there must not be any incomplete lines in the bedfile.

    Returns
    -------
    dict of lists of dicts
        The keys are chromosome names. The values are lists of features for that
        chromosome. The features are represented as dicts with the following
        structure::

            {
                'chrom': str,
                'start': int,
                'end'  : int,
                'id'   : str or None,
                'value': float or None
            }

        The 'id' and 'value' fields may be None if no feature ID's were provided
        in the BED file, but the keys will always be present in the returned
        dict.

    Notes
    -----
    The parser will attempt to guess the column indices of the id and value
    fields based on the number of columns and the types of the column entries.
    """

    # dict to store features
    features = {}

    # parse bedfile
    with open(bedfile, 'r') as handle:
        for line in handle:
            # skip comments and track line
            if line.startswith('#') or line.startswith('track'):
                continue

            # split line
            pieces = line.strip().split('\t')
            if len(pieces) < 3 and not strict:
                continue  # skip incomplete lines when strict=False

            # parse chromosome
            chromosome = pieces[0]

            # add chromosome to dict if this is a new one
            if chromosome not in features:
                features[chromosome] = []

            # parse feature information
            start = int(pieces[1])
            end = int(pieces[2])
            feature_id = None
            value = None

            # user-specified column schema
            if id_index is not None:
                feature_id = pieces[id_index]
            if value_index is not None:
                value = float(pieces[value_index])

            # intelligent column schema guessing
            if not id_index and not value_index:
                if len(pieces) >= 4:
                    try:
                        value = float(pieces[3])
                    except ValueError:
                        feature_id = pieces[3]
                if len(pieces) >= 5:
                    try:
                        value = float(pieces[4])
                    except ValueError:
                        feature_id = pieces[4]

            # dict to represent this feature
            peak_dict = {'chrom': chromosome,
                         'start': start,
                         'end'  : end}

            # add id and value if parsed
            if feature_id is not None:
                peak_dict['id'] = feature_id
            if value is not None:
                peak_dict['value'] = value

            # parse strand information if present
            if len(pieces) >= 6:
                peak_dict['strand'] = pieces[5]

            # add this feature to the list
            if (boundaries is None) or \
                    (count_intersections(peak_dict, boundaries) > 0):
                features[chromosome].append(peak_dict)

    return features


# test client
def main():
    peaks = load_features('test/peaks.bed', id_index=3, value_index=4)['chr1']
    print(len(peaks))
    print(peaks[0])
    peaks = load_features('test/peaks.bed')['chr1']
    print(len(peaks))
    print(peaks[0])
    peaks = load_features('test/reduced_bedgraph.bed', value_index=3)['chr4']
    print(len(peaks))
    print(peaks[0])
    peaks = load_features('test/reduced_bedgraph.bed')['chr4']
    print(len(peaks))
    print(peaks[0])


if __name__ == "__main__":
    main()
