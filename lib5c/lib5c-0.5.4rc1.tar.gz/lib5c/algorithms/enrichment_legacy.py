"""
Legacy module for computing enrichments of annotations within categories of
categorized loops. A newer implementation exists in lib5c.algorithms.enrichment.
"""

import numpy as np
from matplotlib import pyplot as plt
import scipy.stats as stats

from lib5c.parsers.loops import load_loops
from lib5c.parsers.primers import load_primermap
from lib5c.util.annotationmap import make_annotationmaps


def make_intersection_dict(loops, annotationmaps, thresholds=(0,),
                           margins=(0, 1,)):
    """
    Makes a dictionary including information about the intersections of
    different classes of loops with pairs of
    annotations.

    Parameters
    ----------
    loops : dict of dicts of dicts
        The outer keys are loop categories as strings. The next level's keys are
        region names as strings. The innermost dicts represent loops. These
        inner loop dicts have the following structure::

            {
                'x': int,
                'y': int
            }

        The ints represent the x and y coordinate, respectively, of the loop
        within the region. See ``lib5c.enrichment.reshape_loops()``.
    annotationmaps : dict of dict of lists
        The keys of the outer dict are annotation names The values are
        annotationmaps. Annotationmaps are dicts of lists whose keys are region
        names. Their values are lists, where the ith entry represents the number
        of intersections between the annotation and the ith bin of that region.
        See ``lib5c.util.annotationmap.get_single_annotatiomap()`` or
        ``lib5c.util.annotationmap.make_annotationmaps()``.
    thresholds : sequence of ints
        The thresholds to consider when calculating the intersections. A loop is
        considered to be "hit" by an annotation on the x- or y-axis if there are
        more than <threshold> bed features in that bin. A threshold of 0 means
        that the presence of just one annotation in a bin is enough to hit the
        pixel above it. Higher thresholds may be useful for investigating
        intersections with annotations known to have clustered binding sites.
        For example, using a threshold of 2 will only count intersections of
        clusters of the annotation with at least 3 sites in the same bin. This
        kwarg accepts a sequence of thresholds, and the returned data structure
        will include subdicts for each threshold value passed (see below).
    margins : sequence of ints
        The margins of error to use when calculating the intersections. If an
        intersection of two annotations is within <margin> pixels of a
        categorized loop along either axis, it will be considered "close enough"
        or "within the margin of error" and the loop will be counted as hit. A
        margin of 0 implies that there is no margin for error and all loops must
        be hit exactly by the pair of annotations to be counted as hit. This has
        been called "unfeathered" intersection. A margin of 1 implies that as
        long as a pair of annotations hits either the exact pixel of the loop or
        any of the eight pixels surrounding that pixel, the loop will be counted
        as "hit". This has been called "feathered" intersection. This kwarg
        accepts a sequence of margins, and the returned data structure will
        include subdicts for each margin value passed (see below).

    Returns
    -------
    dict of dicts of dicts of dicts of dicts of dicts
        The outer dicts select a pair of annotations, a loop category, a
        threshold, and a margin of error. The inner dict selected by the outer
        keys contains information about the intersection of the given loop
        category with the pair of annotations, where "intersection" is defined
        according to the threshold and margin of error specified (see above).
        The specific order of the outer keys and structure of the innermost dict
        is::

            intersection_dict[annotation on one side : str]\
                             [annotation on the other side : str]\
                             [loop category : str]\
                             [threshold : int]\
                             [margin : int] =\
                {
                    'intersections': int,
                    'percentage': float,
                    'pvalue': {
                        'less': float,
                        'greater': float
                    }
                }

        Here 'intersections' counts the number of loops in the selected category
        hit by the selected pair of annotations according to the definition of
        "hit" as specified by the selected threshold and margin of error.
        'percentage' stores the percentage of all loops in the selected category
        that were hit. 'pvalue' represents the Fisher exact test p-values for
        how often this loop category is hit or not hit by the pair of
        annotations versus how often the loop category called "background" is
        hit or not hit by the pair of annotations. Its subkeys 'less' and
        'greater' represent the left-tail and right-tail p-values, respectively.
        'less' represents the p-value for seeing a lower enrichment of hits in
        the selected category, while 'greater' represents the p-value for seeing
        a greater enrichment of hits in the selected category.
    """
    # set up dict structure
    intersection_dict = _setup_intersection_dict(loops, annotationmaps,
                                                 thresholds, margins)

    # count the intersections
    _count_intersections(intersection_dict, loops, annotationmaps)

    # calculate percentages
    _normalize_intersection_dict(intersection_dict, loops)

    # compute p-values
    _compute_p_values(intersection_dict, loops)
    return intersection_dict


def _setup_intersection_dict(loops, annotationmaps, thresholds, margins):
    """
    Sets up the nested dict structure for the intersection dict. See
    ``lib5c.enrichment.make_intersection_dict()``.
    """
    intersection_dict = {}
    for annotation_a in annotationmaps.keys():
        intersection_dict[annotation_a] = {}
        for annotation_b in annotationmaps.keys():
            intersection_dict[annotation_a][annotation_b] = {}
            for loop_type in loops.keys():
                intersection_dict[annotation_a][annotation_b][loop_type] = {}
                for threshold in thresholds:
                    intersection_dict[annotation_a][annotation_b][loop_type] \
                        [threshold] = {}
                    for margin in margins:
                        intersection_dict[annotation_a][annotation_b] \
                            [loop_type][threshold][margin] = {}
    return intersection_dict


def _count_intersections(intersection_dict, loops, annotationmaps):
    """
    Counts the intersections for each parameter combination and stores them in
    the intersection dict. See ``lib5c.enrichment.make_intersection_dict()``.
    """
    for annotation_a in intersection_dict.keys():
        for annotation_b in intersection_dict[annotation_a].keys():
            for loop_type in intersection_dict[annotation_a] \
                    [annotation_b].keys():
                for threshold in intersection_dict[annotation_a][annotation_b] \
                        [loop_type].keys():
                    for margin in intersection_dict[annotation_a][
                        annotation_b] \
                            [loop_type][threshold].keys():
                        intersections = 0
                        for region in loops[loop_type].keys():
                            for loop in loops[loop_type][region]:
                                a_x = sum(
                                    [annotationmaps[annotation_a][region][index]
                                     for index in range(
                                        max(0, loop['x'] - margin),
                                        min(len(annotationmaps[annotation_a]
                                                [region]),
                                            loop['x'] + margin + 1))])
                                b_x = sum(
                                    [annotationmaps[annotation_b][region][index]
                                     for index in range(
                                        max(0, loop['x'] - margin),
                                        min(len(annotationmaps[annotation_b]
                                                [region]),
                                            loop['x'] + margin + 1))])
                                a_y = sum(
                                    [annotationmaps[annotation_a][region]
                                     [index]
                                     for index in range(
                                        max(0, loop['y'] - margin),
                                        min(len(annotationmaps[annotation_a]
                                                [region]),
                                            loop['y'] + margin + 1))])
                                b_y = sum(
                                    [annotationmaps[annotation_b][region][index]
                                     for index in range(
                                        max(0, loop['y'] - margin),
                                        min(len(annotationmaps[annotation_b]
                                                [region]),
                                            loop['y'] + margin + 1))])
                                if (a_x > threshold and b_y > threshold) or \
                                        (a_y > threshold and b_x > threshold):
                                    intersections += 1
                        selected_dict = intersection_dict[annotation_a] \
                            [annotation_b][loop_type][threshold][margin]
                        selected_dict['intersections'] = intersections

    return intersection_dict


def _normalize_intersection_dict(intersection_dict, loops):
    """
    Calculates the percentages of loops hit for each parameter combination based
    on the number of intersections and stores it in the ``intersection_dict``.
    See ``lib5c.enrichment.make_intersection_dict()``.
    """
    for annotation_a in intersection_dict.keys():
        for annotation_b in intersection_dict[annotation_a].keys():
            for loop_type in intersection_dict[annotation_a] \
                    [annotation_b].keys():
                for threshold in intersection_dict[annotation_a][annotation_b] \
                        [loop_type].keys():
                    for margin in intersection_dict[annotation_a][
                        annotation_b] \
                            [loop_type][threshold].keys():
                        selected_dict = intersection_dict[annotation_a] \
                            [annotation_b][loop_type][threshold][margin]
                        selected_dict['percentage'] = \
                            selected_dict['intersections'] / \
                            float(len([x
                                       for region in loops[loop_type].keys()
                                       for x in loops[loop_type][region]]))


def _compute_p_values(intersection_dict, loops):
    """
    Calculates the p-values for seeing the numbers of loops hit versus not hit
    in the specified class versus the background class using Fisher's exact test
    for each parameter combination based on the number of intersections and
    stores it in the ``intersection_dict``. See
    ``lib5c.enrichment.make_intersection_dict()``.
    """
    for annotation_a in intersection_dict.keys():
        for annotation_b in intersection_dict[annotation_a].keys():
            for loop_type in intersection_dict[annotation_a] \
                    [annotation_b].keys():
                for threshold in intersection_dict[annotation_a][annotation_b] \
                        [loop_type].keys():
                    for margin in intersection_dict[annotation_a][
                        annotation_b] \
                            [loop_type][threshold].keys():
                        selected_dict = intersection_dict[annotation_a] \
                            [annotation_b][loop_type][threshold][margin]
                        background_dict = intersection_dict[annotation_a] \
                            [annotation_b]['background'][threshold][margin]
                        selected_dict['pvalue'] = {}
                        one_one = selected_dict['intersections']
                        one_two = background_dict['intersections']
                        col_one_sum = len([x
                                           for region in loops[loop_type].keys()
                                           for x in loops[loop_type][region]])
                        col_two_sum = len(
                            [x
                             for region in loops['background'].keys()
                             for x in loops['background'][region]])
                        two_one = col_one_sum - one_one
                        two_two = col_two_sum - one_two
                        if one_one == 0 and one_two == 0:
                            selected_dict['pvalue']['less'] = 0.5
                            selected_dict['pvalue']['greater'] = 0.5
                        else:
                            cont_table = [[one_one, one_two],
                                          [two_one, two_two]]
                            oddsratio, p_l = stats.fisher_exact(
                                cont_table, alternative='less')
                            oddsratio, p_g = stats.fisher_exact(
                                cont_table, alternative='greater')
                            selected_dict['pvalue']['less'] = p_l
                            selected_dict['pvalue']['greater'] = p_g


def plot_looptype_vs_annotation_heatmap(intersection_dict, filename,
                                        constant_annotation,
                                        loop_type_order=None,
                                        annotation_order=None, threshold=0,
                                        margin=0):
    """
    Plots a heatmap with loop types arranged on the x-axis and annotations
    arranged on the y-axis, with the other side of the annotation being
    specified and held constant.

    Parameters
    ----------
    intersection_dict : dict of dicts of dicts of dicts of dicts of dicts
        Dictionary containing information about intersections to use as a data
        source for this heatmap. See
        ``lib5c.util.enrichment.make_intersection_dict()``.
    filename : str
        String reference to the filename to draw the heatmap to. If you don't
        specify an extension, .png will be appended. Pass a string ending in
        '.eps' to write the heatmap as a vector graphics file.
    constant_annotation : str
        the annotation to always look for on one side of the loop throughout the
        whole heatmap. The annotation to look for on the other side will be
        varied along the y-axis.
    loop_type_order : list of str or None
        The order in which to arrange the loop types along the x-axis, from left
        to right. If you exclude a loop type from this list, it will be excluded
        from the heatmap. Pass None to automatically infer the loop types from
        the intersection_dict.
    annotation_order : list of str or None
        The order in which to arrange the annotations on the y-axis, from bottom
        to top. If you exclude an annotation from this list, it will be excluded
        from the heatmap. Pass None to automatically infer the annotations from
        the intersection_dict.
    threshold : int
        The threshold to use to determine what counts as an intersection. The
        intersection_dict must contain this value in its list of thresholds. See
        ``lib5c.util.enrichment.make_intersection_dict()``.
    margin : int
        The margin of error to use to determine what counts as an intersection.
        The intersection_dict must contain this value in its list of margins of
        error. See ``lib5c.util.enrichment.make_intersection_dict()``.
    """
    # auto-set loop_type_order and annotation_order if necessary
    if not annotation_order:
        annotation_order = intersection_dict.keys()
    if not loop_type_order:
        loop_type_order = intersection_dict[annotation_order[0]] \
            [annotation_order[0]].keys()

    # prepare array for imshow
    array = []
    for i in range(len(annotation_order)):
        row = []
        for j in range(len(loop_type_order)):
            selected_dict = intersection_dict[annotation_order[i]] \
                [constant_annotation][loop_type_order[j]][threshold][margin]
            background_dict = intersection_dict[annotation_order[i]] \
                [constant_annotation]['background'][threshold][margin]
            if background_dict['percentage']:
                fold_enrichment = selected_dict['percentage'] / \
                    float(background_dict['percentage'])
                if fold_enrichment:
                    row.append(np.log2(fold_enrichment))
                else:
                    row.append(np.log2(0.0001))
            else:
                row.append(0)
        array.append(row)

    # prepare pvalue array
    p_values = []
    for i in range(len(annotation_order)):
        row = []
        for j in range(len(loop_type_order)):
            selected_dict = intersection_dict[annotation_order[i]] \
                [constant_annotation][loop_type_order[j]][threshold][margin]
            row.append(min(selected_dict['pvalue']['less'],
                           selected_dict['pvalue']['greater']))
        p_values.append(row)

    # plot heatmap
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(72 / 60.0 * len(annotation_order),
                        40 / 60.0 * len(annotation_order))
    cmap = plt.get_cmap('bwr')
    im = plt.imshow(array, interpolation='none', cmap=cmap, origin='lower',
                    vmin=-2.0, vmax=2.0)
    for i in range(len(annotation_order)):
        for j in range(len(loop_type_order)):
            text = ''
            if p_values[i][j] >= 0.9:
                text = '1.0'
            elif p_values[i][j] >= 0.1:
                text = '0.%i' % (int(10 * p_values[i][j]) + 1)
            elif p_values[i][j] >= 0.01:
                if p_values[i][j] >= 0.09:
                    text = '0.1'
                else:
                    text = '0.0%i' % (int(100 * p_values[i][j]) + 1)
            else:
                text = 'E-%i' % int(-np.log10(p_values[i][j]))
            plt.text(j, i, text, ha='center', va='center')
    plt.colorbar(im)
    plt.xticks(np.arange(len(loop_type_order)), loop_type_order, rotation=45,
               ha='right')
    plt.yticks(np.arange(len(annotation_order)), annotation_order)
    plt.savefig(filename, bbox_inches='tight')


def plot_annotation_vs_annotation_heatmap(intersection_dict, filename,
                                          loop_type, axis_order=None,
                                          threshold=0, margin=1):
    """
    Plots a heatmap with annotations arranged on both the x- and the y-axis,
    showing enrichments for all pairs of those annotations among loops of a
    specified class.

    Parameters
    ----------
    intersection_dict : dict of dicts of dicts of dicts of dicts of dicts
        Dictionary containing information about intersections to use as a data
        source for this heatmap. See
        ``lib5c.util.enrichment.make_intersection_dict()``.
    filename : str
        String reference to the filename to draw the heatmap to. If you don't
        specify an extension, .png will be appended. Pass a string ending in
        '.eps' to write the heatmap as a vector graphics file.
    loop_type : str
        The loop type to consider in this heatmap.
    axis_order : list of str or None
        The order in which to arrange the annotations on the x-axis, from left
        to right, and the y-axis, from bottom to top. If you exclude an
        annotation from this list, it will be excluded from the heatmap. Pass
        None to automatically infer the annotations from the
        ``intersection_dict``.
    threshold : int
        The threshold to use to determine what counts as an intersection. The
        intersection_dict must contain this value in its list of thresholds. See
        ``lib5c.util.enrichment.make_intersection_dict()``.
    margin : int
        The margin of error to use to determine what counts as an intersection.
        The intersection_dict must contain this value in its list of margins of
        error. See ``lib5c.util.enrichment.make_intersection_dict()``.
    """
    # auto-set axis_order if necessary
    if not axis_order:
        axis_order = intersection_dict.keys()

    # prepare array for imshow
    array = []
    for i in range(len(axis_order)):
        row = []
        for j in range(len(axis_order)):
            selected_dict = intersection_dict[axis_order[i]][axis_order[j]] \
                [loop_type][threshold][margin]
            background_dict = intersection_dict[axis_order[i]][axis_order[j]] \
                ['background'][threshold][margin]
            if background_dict['percentage']:
                fold_enrichment = selected_dict['percentage'] / \
                    float(background_dict['percentage'])
                if fold_enrichment:
                    row.append(np.log2(fold_enrichment))
                else:
                    row.append(np.log2(0.0001))
            else:
                row.append(0)
        array.append(row)

    # prepare pvalue array
    p_values = []
    for i in range(len(axis_order)):
        row = []
        for j in range(len(axis_order)):
            selected_dict = intersection_dict[axis_order[i]][axis_order[j]] \
                [loop_type][threshold][margin]
            row.append(min(selected_dict['pvalue']['less'],
                           selected_dict['pvalue']['greater']))
        p_values.append(row)

    # plot heatmap
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(72 / 60.0 * len(axis_order), 40 / 60.0 * len(
        axis_order))
    cmap = plt.get_cmap('bwr')
    im = plt.imshow(array, interpolation='none', cmap=cmap, origin='lower',
                    vmin=-2.0, vmax=2.0)
    for i in range(len(array)):
        for j in range(len(array)):
            text = ''
            if p_values[i][j] >= 0.9:
                text = '1.0'
            elif p_values[i][j] >= 0.1:
                text = '0.%i' % (int(10 * p_values[i][j]) + 1)
            elif p_values[i][j] >= 0.01:
                if p_values[i][j] >= 0.09:
                    text = '0.1'
                else:
                    text = '0.0%i' % (int(100 * p_values[i][j]) + 1)
            else:
                text = 'E-%i' % int(-np.log10(p_values[i][j]))
            plt.text(j, i, text, ha='center', va='center')
    plt.colorbar(im)
    plt.xticks(np.arange(len(axis_order)), axis_order, rotation=45, ha='right')
    plt.yticks(np.arange(len(axis_order)), axis_order)
    plt.savefig(filename, bbox_inches='tight')


# test client
def main():
    loops = load_loops('test/triloops.txt')
    pixelmap = load_primermap('test/bins.bed')
    annotationmaps = make_annotationmaps(
        pixelmap, directory='test/annotations', add_wildcard=True)

    intersection_dict = make_intersection_dict(loops, annotationmaps)

    plot_looptype_vs_annotation_heatmap(
        intersection_dict, 'test/enrichments_unsided.png', 'wildcard')
    plot_annotation_vs_annotation_heatmap(
        intersection_dict, 'test/enrichments_sided.png', 'wt_only')


if __name__ == "__main__":
    main()
