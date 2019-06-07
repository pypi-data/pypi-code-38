"""
Module containing utilities for constructing annotatiomaps.

Annotatiomaps record the number of BED features of a certain type present at a
given linear bin as specified by a pixelmap.
"""

import glob
import os

import numpy as np

from lib5c.parsers.bed import load_features
from lib5c.util.bed import count_intersections


def make_single_annotationmap(annotation, pixelmap):
    """
    Generates an annotationmap given an annotation and a pixelmap.

    Parameters
    ----------
    annotation : dict of lists of dicts
        The keys are chromosome names. The values are lists of features for that
        chromosome. The features are represented as dicts with the following
        structure::

            {
                'chrom': str
                'start': int,
                'end'  : int,
            }

        See ``lib5c.parsers.bed.load_features()``.
    pixelmap: pixelmap
        The pixelmap to use to generate the annotationmap. See
        ``lib5c.parsers.bed.get_pixelmap()``.

    Returns
    -------
    dict of lists
        The keys of the dictionary are region names. The values are lists, where
        the ``i`` th entry represents the number of intersections between the
        annotation and the ``i`` th bin of that region.
    """
    annotationmap = {}
    for region in pixelmap:
        annotationmap[region] = []
        for i in range(len(pixelmap[region])):
            if pixelmap[region][i]['chrom'] in annotation:
                annotationmap[region].append(
                    count_intersections(
                        pixelmap[region][i],
                        annotation[pixelmap[region][i]['chrom']]))
            else:
                annotationmap[region].append(0)
        annotationmap[region] = np.array(annotationmap[region])
    return annotationmap


def make_annotationmaps(pixelmap, directory='./annotations', add_wildcard=True):
    """
    Gets a dict of annotationmaps, one for every BED file in a specified
    directory.

    Parameters
    ----------
    pixelmap: pixelmap
        The pixelmap to use to generate the annotationmap. See
        ``lib5c.parsers.bed.get_pixelmap()``.
    directory: str
        The directory to look in for BED files describing the annotations.
    add_wildcard : bool
        Pass True to add a 'wildcard' annotation that has 100 hits in every bin.
        Useful for doing "unsided" enrichments later.

    Returns
    -------
    dict of dict of lists
        The keys of the outer dict are annotation names as parsed from the names
        of the BED files in directory. The values are annotationmaps. See
        ``lib5c.util.annotationmap.get_single_annotatiomap()``.
    """
    # normalize directory
    directory = os.path.normcase(directory)

    # annotatopmaps to return
    annotationmaps = {}

    # make annotationmaps
    for path in glob.glob('%s/*.bed' % directory) + \
            glob.glob('%s/*.interval' % directory):
        annotation = load_features(path)
        name = os.path.splitext(os.path.split(path)[-1])[0]
        annotationmap = make_single_annotationmap(annotation, pixelmap)
        annotationmaps[name] = annotationmap

    # add wildcard if desired
    if annotationmaps and add_wildcard:
        any_key = annotationmaps.keys()[0]
        annotationmaps['wildcard'] = {}
        for region in annotationmaps[any_key].keys():
            annotationmaps['wildcard'][region] = np.array(
                [100] * len(annotationmaps[any_key][region]))

    return annotationmaps


# test client
def main():
    # we'll need a pixelmap
    from lib5c.parsers.primers import load_primermap
    pixelmap = load_primermap('test/bins.bed')

    # directory where we should look for annotations
    directory = 'test/annotations'

    # make the annotationmaps
    annotationmaps = make_annotationmaps(pixelmap, directory)

    # prove that we have the annotationmap
    print(annotationmaps.keys())
    for key in annotationmaps.keys():
        print('%s %i' % (key, annotationmaps[key]['Sox2'][45]))


if __name__ == "__main__":
    main()
