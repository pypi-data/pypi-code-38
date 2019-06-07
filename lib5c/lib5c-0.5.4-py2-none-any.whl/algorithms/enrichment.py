"""
Module for computing enrichments of annotations within categories of categorized
loops.
"""

from __future__ import division

import numpy as np
from scipy.ndimage import generic_filter
import scipy.stats as stats

from lib5c.util.lru_cache import lru_cache


@lru_cache(maxsize=None)
def process_annotations(annotation_label, region, annotationmaps, threshold=0,
                        margin=1):
    """
    Extracts one annotation and one region from a dict of annotationmaps and
    returns it in a vector form.

    This function should be called from within the bodies of vectorized
    enrichment functions that accept standard annotationmaps as arguments.

    Parameters
    ----------
    annotation_label : str
        The annotation for which a vector should be created. Must be a key of
        ``annotationmaps``.
    region : str
        The specific region for which a vector should be created. Must be a key
        of ``annotationmaps[annotation_label]``.
    annotationmaps : dict of annotationmap
        A dict describing the annotations. In total, it should have the
        following structure::

            {
                'annotation_a_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                 },
                'annotation_b_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                },
                ...
            }

        where ``annotationmaps['annotation_a']['region_r']`` should be a list of
        ints describing the number of ``'annotation_a'``s present in each bin of
        ``'region_r'``.
    threshold : int
        Bins are defined to contain an annotation if they are "hit" strictly
        more than ``threshold`` times by the annotation.
    margin : int
        A bin is defined to contain an annotation if any bin within ``margin``
        bins is "hit" by the annotation. Corresponds to a "margin for error" in
        the intersection precision.

    Returns
    -------
    np.ndarray
        The processed vector representing the coverage of the selected
        annotation across the selected region, according to the definitions
        implied by the choise of ``threshold`` and ``margin``.

    Examples
    --------
    >>> annotationmaps = {'a': {'r1': [0, 0, 2, 1]}}
    >>> process_annotations('a', 'r1', annotationmaps)
    array([0, 1, 1, 1])
    >>> process_annotations('a', 'r1', annotationmaps, threshold=1, margin=0)
    array([0, 0, 1, 0])
    """
    return generic_filter(annotationmaps[annotation_label][region],
                          lambda x: x.sum() > threshold, size=1+2*margin,
                          mode='constant')


@lru_cache(maxsize=None)
def count_intersections(annotation_a, annotation_b, region, category,
                        annotationmaps, looping_classes, threshold=0, margin=1,
                        asymmetric=False):
    """
    Counts the number of times one annotation intersects another at a particular
    category of called loops within a specified region.

    Parameters
    ----------
    annotation_a : str
        The annotation to look for on one side of the loop. Must be a key into
        ``annotationmaps``.
    annotation_b : str
        The annotation to look for on the other side of the loop. Must be a key
        into ``annotationmaps``.
    region : str
        The region to count intersections over.
    category : str
        The loop category to count intersections for.
    annotationmaps : dict of annotationmap
        A dict describing the annotations. In total, it should have the
        following structure::

            {
                'annotation_a_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                 },
                'annotation_b_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                },
                ...
            }

        where ``annotationmaps['annotation_a']['region_r']`` should be a list of
        ints describing the number of ``'annotation_a'``s present in each bin of
        ``'region_r'``.
    looping_classes : dict of np.ndarray with str dtype
        The keys should be region names as strings, the values should be square,
        symmetric arrays of the same size and shape as the indicated region,
        with string loop category names in the positions of categorized loops.
    threshold : int
        Bins are defined to contain an annotation if they are "hit" strictly
        more than ``threshold`` times by the annotation.
    margin : int
        A bin is defined to contain an annotation if any bin within ``margin``
        bins is "hit" by the annotation. Corresponds to a "margin for error" in
        the intersection precision.
    asymmetric : bool
        Pass True to only count situations when A is upstream of B. Pass False
        to count intersections regardless of order.

    Returns
    -------
    int
        The total number of intersections.

    Examples
    --------
    >>> import numpy as np
    >>> clear_enrichment_caches()
    >>> annotationmaps = {'a': {'r1': [0, 0, 2, 1]},
    ...                   'b': {'r1': [1, 1, 0, 0]}}
    >>> looping_classes = {'r1': np.array([[''   , ''   , 'es' , 'ips'],
    ...                                    [''   , ''   , 'npc', 'npc'],
    ...                                    ['es' , 'npc', ''   , ''   ],
    ...                                    ['ips', 'npc', ''   , ''   ]],
    ...                                   dtype='a25')}
    >>> count_intersections('a', 'b', 'r1', 'es', annotationmaps,
    ...                     looping_classes, margin=0)
    1
    >>> count_intersections('a', 'b', 'r1', 'npc', annotationmaps,
    ...                     looping_classes, margin=0)
    2
    >>> count_intersections('a', 'b', 'r1', 'npc', annotationmaps,
    ...                     looping_classes, margin=0)
    2
    >>> count_intersections.cache_info()
    CacheInfo(hits=1, misses=2, maxsize=None, currsize=2)
    >>> count_intersections('a', 'b', 'r1', 'es', annotationmaps,
    ...                     looping_classes, margin=0, asymmetric=True)
    0
    >>> count_intersections('b', 'a', 'r1', 'es', annotationmaps,
    ...                     looping_classes, margin=0, asymmetric=True)
    1
    """
    temp = np.outer(
        process_annotations(annotation_a, region, annotationmaps,
                            threshold=threshold, margin=margin),
        process_annotations(annotation_b, region, annotationmaps,
                            threshold=threshold, margin=margin)) > 0
    if not asymmetric:
        return np.tril(looping_classes[region] == category)[temp | temp.T].sum()
    return np.tril(looping_classes[region] == category)[temp.T].sum()


@lru_cache(maxsize=None)
def count_intersections_all(annotation_a, annotation_b, category,
                            annotationmaps, looping_classes, threshold=0,
                            margin=1, asymmetric=False):
    """
    Counts the number of times ``annotation_a`` and ``annotation_b`` are found
    on opposite ends of loops in a given category of loop type across all
    genomic regions.

    Parameters
    ----------
    annotation_a : str
        Annotation to look for on one side of the loop.
    annotation_b : str
        Annotation to look for on the other side of the loop.
    category : str
        Only consider loops of this category.
    annotationmaps : dict of annotationmap
        A dict describing the annotations. In total, it should have the
        following structure::

            {
                'annotation_a_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                 },
                'annotation_b_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                },
                ...
            }

        where ``annotationmaps['annotation_a']['region_r']`` should be a list of
        ints describing the number of ``'annotation_a'``s present in each bin of
        ``'region_r'``.
    looping_classes : dict of np.ndarray with str dtype
        The keys should be region names as strings, the values should be square,
        symmetric arrays of the same size and shape as the indicated region,
        with string loop category names in the positions of categorized loops.
    threshold : int
        Bins are defined to contain an annotation if they are "hit" strictly
        more than ``threshold`` times by the annotation.
    margin : int
        A bin is defined to contain an annotation if any bin within ``margin``
        bins is "hit" by the annotation. Corresponds to a "margin for error" in
        the intersection precision.
    asymmetric : bool
        Pass True to only count situations when A is upstream of B. Pass False
        to count intersections regardless of order.

    Returns
    -------
    int
        The total number of intersections across all regions.

    Examples
    --------
    >>> import numpy as np
    >>> annotationmaps = {'a': {'r1': [0, 0, 2], 'r2': [1, 0]},
    ...                   'b': {'r1': [1, 1, 0], 'r2': [0, 1]}}
    >>> looping_classes = {'r1': np.array([['npc', ''   , 'es' ],
    ...                                    [''   , ''   , 'npc'],
    ...                                    ['es' , 'npc', ''   ]],
    ...                                   dtype='a25'),
    ...                    'r2': np.array([[''   , 'es' ],
    ...                                    ['es' , ''   ]],
    ...                                   dtype='a25')}
    >>> count_intersections_all('a', 'b', 'es', annotationmaps,
    ...                         looping_classes, margin=0)
    2
    >>> count_intersections_all('a', 'b', 'npc', annotationmaps,
    ...                         looping_classes, margin=0)
    1
    """
    all_intersections = 0
    for region in looping_classes.keys():
        all_intersections += count_intersections(
            annotation_a, annotation_b, region, category, annotationmaps,
            looping_classes, threshold=threshold, margin=margin,
            asymmetric=asymmetric)
    return all_intersections


@lru_cache(maxsize=None)
def get_annotation_percentage(annotation_a, annotation_b, region, category,
                              annotationmaps, looping_classes, threshold=0,
                              margin=1, asymmetric=False):
    """
    Computes the precentage of loops within a particular region categorized into
    a particular category that represent loops between ``annotation_a`` and
    ``annotation_b``.

    Parameters
    ----------
    annotation_a : str
        Annotation to look for on one side of the loop.
    annotation_b : str
        Annotation to look for on the other side of the loop.
    region : str
        The region to compute the percentage within.
    category : str
        The category of loops to consider.
    annotationmaps : dict of annotationmap
        A dict describing the annotations. In total, it should have the
        following structure::

            {
                'annotation_a_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                 },
                'annotation_b_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                },
                ...
            }

        where ``annotationmaps['annotation_a']['region_r']`` should be a list of
        ints describing the number of ``'annotation_a'``s present in each bin of
        ``'region_r'``.
    looping_classes : dict of np.ndarray with str dtype
        The keys should be region names as strings, the values should be square,
        symmetric arrays of the same size and shape as the indicated region,
        with string loop category names in the positions of categorized loops.
    threshold : int
        Bins are defined to contain an annotation if they are "hit" strictly
        more than ``threshold`` times by the annotation.
    margin : int
        A bin is defined to contain an annotation if any bin within ``margin``
        bins is "hit" by the annotation. Corresponds to a "margin for error" in
        the intersection precision.
    asymmetric : bool
        Pass True to only count situations when A is upstream of B. Pass False
        to count intersections regardless of order.

    Returns
    -------
    float
        The fraction of loops within the region of the specified category that
        represent loops between the indicated annotations.

    Examples
    --------
    >>> import numpy as np
    >>> annotationmaps = {'a': {'r1': [0, 0, 0, 1]},
    ...                   'b': {'r1': [1, 1, 0, 0]}}
    >>> looping_classes = {'r1': np.array([[''   , ''   , 'es' , 'ips'],
    ...                                    [''   , ''   , 'npc', 'npc'],
    ...                                    ['es' , 'npc', ''   , ''   ],
    ...                                    ['ips', 'npc', ''   , ''   ]],
    ...                                   dtype='a25')}
    >>> get_annotation_percentage('a', 'b', 'r1', 'ips', annotationmaps,
    ...                           looping_classes, margin=0)
    1.0
    >>> get_annotation_percentage('a', 'b', 'r1', 'npc', annotationmaps,
    ...                           looping_classes, margin=0)
    0.5
    """
    return (count_intersections(annotation_a, annotation_b, region, category,
                                annotationmaps, looping_classes,
                                threshold=threshold, margin=margin,
                                asymmetric=asymmetric) /
            np.tril(looping_classes[region] == category).sum())


@lru_cache(maxsize=None)
def get_annotation_percentage_all(annotation_a, annotation_b, category,
                                  annotationmaps, looping_classes, threshold=0,
                                  margin=1, asymmetric=False):
    """
    Computes the precentage of loops across all regions categorized into a
    particular category that represent loops between ``annotation_a`` and
    ``annotation_b``.

    Parameters
    ----------
    annotation_a : str
        Annotation to look for on one side of the loop.
    annotation_b : str
        Annotation to look for on the other side of the loop.
    category : str
        The category of loops to consider.
    annotationmaps : dict of annotationmap
        A dict describing the annotations. In total, it should have the
        following structure::

            {
                'annotation_a_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                 },
                'annotation_b_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                },
                ...
            }

        where ``annotationmaps['annotation_a']['region_r']`` should be a list of
        ints describing the number of ``'annotation_a'``s present in each bin of
        ``'region_r'``.
    looping_classes : dict of np.ndarray with str dtype
        The keys should be region names as strings, the values should be square,
        symmetric arrays of the same size and shape as the indicated region,
        with string loop category names in the positions of categorized loops.
    threshold : int
        Bins are defined to contain an annotation if they are "hit" strictly
        more than ``threshold`` times by the annotation.
    margin : int
        A bin is defined to contain an annotation if any bin within ``margin``
        bins is "hit" by the annotation. Corresponds to a "margin for error" in
        the intersection precision.
    asymmetric : bool
        Pass True to only count situations when A is upstream of B. Pass False
        to count intersections regardless of order.

    Returns
    -------
    float
        The fraction of loops across all regions of the specified category that
        represent loops between the indicated annotations.

    Examples
    --------
    >>> import numpy as np
    >>> annotationmaps = {'a': {'r1': [0, 0, 2], 'r2': [1, 0]},
    ...                   'b': {'r1': [1, 1, 0], 'r2': [0, 1]}}
    >>> looping_classes = {'r1': np.array([['npc', ''   , 'es' ],
    ...                                    [''   , ''   , 'npc'],
    ...                                    ['es' , 'npc', ''   ]],
    ...                                   dtype='a25'),
    ...                    'r2': np.array([['npc', 'es' ],
    ...                                    ['es' , 'npc']],
    ...                                   dtype='a25')}
    >>> get_annotation_percentage_all('a', 'b', 'es', annotationmaps,
    ...                               looping_classes, margin=0)
    1.0
    >>> get_annotation_percentage_all('a', 'b', 'npc', annotationmaps,
    ...                               looping_classes, margin=0)
    0.25
    """
    all_interactions = 0
    for region in looping_classes.keys():
        all_interactions += np.tril(looping_classes[region] == category).sum()
    return (count_intersections_all(annotation_a, annotation_b, category,
                                    annotationmaps, looping_classes,
                                    threshold=threshold, margin=margin,
                                    asymmetric=asymmetric) /
            all_interactions)


@lru_cache(maxsize=None)
def get_fold_change(annotation_a, annotation_b, region, category,
                    annotationmaps, looping_classes, threshold=0, margin=1,
                    asymmetric=False):
    """
    Computes the fold enrichment of the percentage of loops of a particular
    category in a particular region connecting specified annotations relative
    to the special "background" reference category.

    Parameters
    ----------
    annotation_a : str
        Annotation to look for on one side of the loop.
    annotation_b : str
        Annotation to look for on the other side of the loop.
    region : str
        The region to compute the fold enrichment within.
    category : str
        The category of loops to consider.
    annotationmaps : dict of annotationmap
        A dict describing the annotations. In total, it should have the
        following structure::

            {
                'annotation_a_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                 },
                'annotation_b_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                },
                ...
            }

        where ``annotationmaps['annotation_a']['region_r']`` should be a list of
        ints describing the number of ``'annotation_a'``s present in each bin of
        ``'region_r'``.
    looping_classes : dict of np.ndarray with str dtype
        The keys should be region names as strings, the values should be square,
        symmetric arrays of the same size and shape as the indicated region,
        with string loop category names in the positions of categorized loops.
    threshold : int
        Bins are defined to contain an annotation if they are "hit" strictly
        more than ``threshold`` times by the annotation.
    margin : int
        A bin is defined to contain an annotation if any bin within ``margin``
        bins is "hit" by the annotation. Corresponds to a "margin for error" in
        the intersection precision.
    asymmetric : bool
        Pass True to only count situations when A is upstream of B. Pass False
        to count intersections regardless of order.

    Returns
    -------
    float
        The fold enrichment.

    Examples
    --------
    >>> import numpy as np
    >>> annotationmaps = {'a': {'r1': [1, 0, 0, 1]},
    ...                   'b': {'r1': [1, 1, 0, 0]}}
    >>> looping_classes = {'r1': np.array([[''   , ''   , 'es' , 'ips'],
    ...                                    [''   , ''   , 'npc', 'npc'],
    ...                                    ['es' , 'npc', ''   , ''   ],
    ...                                    ['ips', 'npc', ''   , ''   ]],
    ...                                   dtype='a25')}
    >>> looping_classes['r1'][looping_classes['r1'] == ''] = 'background'
    >>> get_fold_change('a', 'b', 'r1', 'ips', annotationmaps, looping_classes,
    ...                 margin=0)
    3.0
    >>> get_fold_change('a', 'b', 'r1', 'npc', annotationmaps, looping_classes,
    ...                 margin=0)
    1.5
    """
    return (get_annotation_percentage(annotation_a, annotation_b, region,
                                      category, annotationmaps, looping_classes,
                                      threshold=threshold, margin=margin,
                                      asymmetric=asymmetric) /
            get_annotation_percentage(annotation_a, annotation_b, region,
                                      'background', annotationmaps,
                                      looping_classes, threshold=threshold,
                                      margin=margin, asymmetric=asymmetric))


@lru_cache(maxsize=None)
def get_fold_change_all(annotation_a, annotation_b, category, annotationmaps,
                        looping_classes, threshold=0, margin=1,
                        asymmetric=False):
    """
    Computes the fold enrichment of the percentage of loops of a particular
    category across all regions connecting specified annotations relative to the
    special "background" reference category.

    Parameters
    ----------
    annotation_a : str
        Annotation to look for on one side of the loop.
    annotation_b : str
        Annotation to look for on the other side of the loop.
    category : str
        The category of loops to consider.
    annotationmaps : dict of annotationmap
        A dict describing the annotations. In total, it should have the
        following structure::

            {
                'annotation_a_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                 },
                'annotation_b_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                },
                ...
            }

        where ``annotationmaps['annotation_a']['region_r']`` should be a list of
        ints describing the number of ``'annotation_a'``s present in each bin of
        ``'region_r'``.
    looping_classes : dict of np.ndarray with str dtype
        The keys should be region names as strings, the values should be square,
        symmetric arrays of the same size and shape as the indicated region,
        with string loop category names in the positions of categorized loops.
    threshold : int
        Bins are defined to contain an annotation if they are "hit" strictly
        more than ``threshold`` times by the annotation.
    margin : int
        A bin is defined to contain an annotation if any bin within ``margin``
        bins is "hit" by the annotation. Corresponds to a "margin for error" in
        the intersection precision.
    asymmetric : bool
        Pass True to only count situations when A is upstream of B. Pass False
        to count intersections regardless of order.

    Returns
    -------
    float
        The fold enrichment.

    Examples
    --------
    >>> import numpy as np
    >>> annotationmaps = {'a': {'r1': [0, 1, 2], 'r2': [1, 0]},
    ...                   'b': {'r1': [1, 1, 0], 'r2': [0, 1]}}
    >>> looping_classes = {'r1': np.array([['npc', ''   , 'es' ],
    ...                                    [''   , ''   , 'npc'],
    ...                                    ['es' , 'npc', ''   ]],
    ...                                   dtype='a25'),
    ...                    'r2': np.array([['ips', 'es' ],
    ...                                    ['es' , ''   ]],
    ...                                   dtype='a25')}
    >>> looping_classes['r1'][looping_classes['r1'] == ''] = 'background'
    >>> looping_classes['r2'][looping_classes['r2'] == ''] = 'background'
    >>> get_fold_change_all('a', 'b', 'es', annotationmaps, looping_classes,
    ...                     margin=0)
    2.0
    >>> get_fold_change_all('a', 'b', 'npc', annotationmaps, looping_classes,
    ...                     margin=0)
    1.0
    >>> get_fold_change_all('a', 'b', 'ips', annotationmaps, looping_classes,
    ...                     margin=0)
    0.0
    """
    denominator = get_annotation_percentage_all(
        annotation_a, annotation_b, 'background', annotationmaps,
        looping_classes, threshold=threshold, margin=margin,
        asymmetric=asymmetric)
    if denominator == 0:
        return 0
    numerator = get_annotation_percentage_all(
        annotation_a, annotation_b, category, annotationmaps, looping_classes,
        threshold=threshold, margin=margin, asymmetric=asymmetric)
    return numerator / denominator


@lru_cache(maxsize=None)
def get_fisher_exact_pvalue(annotation_a, annotation_b, region, category,
                            annotationmaps, looping_classes, threshold=0,
                            margin=1, asymmetric=False):
    """
    Use Fisher's exact test to compute a one-sided p-value against the null
    hypothesis that the selected loop category's overlap with selected
    annotations in a chosen region is the same as the special "background"
    reference loop category's overlap with the same annotations.

    Parameters
    ----------
    annotation_a : str
        Annotation to look for on one side of the loop.
    annotation_b : str
        Annotation to look for on the other side of the loop.
    region : str
        The region to compute the p-value within
    category : str
        The category of loops to consider.
    annotationmaps : dict of annotationmap
        A dict describing the annotations. In total, it should have the
        following structure::

            {
                'annotation_a_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                 },
                'annotation_b_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                },
                ...
            }

        where ``annotationmaps['annotation_a']['region_r']`` should be a list of
        ints describing the number of ``'annotation_a'``s present in each bin of
        ``'region_r'``.
    looping_classes : dict of np.ndarray with str dtype
        The keys should be region names as strings, the values should be square,
        symmetric arrays of the same size and shape as the indicated region,
        with string loop category names in the positions of categorized loops.
    threshold : int
        Bins are defined to contain an annotation if they are "hit" strictly
        more than ``threshold`` times by the annotation.
    margin : int
        A bin is defined to contain an annotation if any bin within ``margin``
        bins is "hit" by the annotation. Corresponds to a "margin for error" in
        the intersection precision.
    asymmetric : bool
        Pass True to only count situations when A is upstream of B. Pass False
        to count intersections regardless of order.

    Returns
    -------
    float
        The p-value.

    Examples
    --------
    >>> import numpy as np
    >>> annotationmaps = {'a': {'r1': [1, 0, 0, 1]},
    ...                   'b': {'r1': [1, 1, 0, 0]}}
    >>> looping_classes = {'r1': np.array([[''   , ''   , 'es' , 'ips'],
    ...                                    [''   , ''   , 'npc', 'npc'],
    ...                                    ['es' , 'npc', ''   , ''   ],
    ...                                    ['ips', 'npc', ''   , ''   ]],
    ...                                   dtype='a25')}
    >>> looping_classes['r1'][looping_classes['r1'] == ''] = 'background'
    >>> get_fisher_exact_pvalue('a', 'b', 'r1', 'ips', annotationmaps,
    ...                         looping_classes, margin=0)
    0.428571428571428...
    >>> get_fisher_exact_pvalue('a', 'b', 'r1', 'npc', annotationmaps,
    ...                         looping_classes, margin=0)
    0.642857142857142...
    """
    # count loops in the specified category
    category_loops_total = np.tril(looping_classes[region] == category).sum()
    category_loops_hit = count_intersections(
        annotation_a, annotation_b, region, category, annotationmaps,
        looping_classes, threshold=threshold, margin=margin,
        asymmetric=asymmetric)
    category_loops_not_hit = category_loops_total - category_loops_hit

    # count loops in the background category
    bkgd_loops_total = np.tril(looping_classes[region] == 'background').sum()
    bkgd_loops_hit = count_intersections(
        annotation_a, annotation_b, region, 'background', annotationmaps,
        looping_classes, threshold=threshold, margin=margin,
        asymmetric=asymmetric)
    bkgd_loops_not_hit = bkgd_loops_total - bkgd_loops_hit

    # short-circuit if neither category nor background have any hits
    if category_loops_hit == 0 and bkgd_loops_hit == 0:
        return 0.5

    # assemble contingency table
    cont_table = [[category_loops_hit, bkgd_loops_hit],
                  [category_loops_not_hit, bkgd_loops_not_hit]]

    # return the smaller of the two single-tailed p-values
    return min(stats.fisher_exact(cont_table, alternative='less')[1],
               stats.fisher_exact(cont_table, alternative='greater')[1])


@lru_cache(maxsize=None)
def get_fisher_exact_pvalue_all(annotation_a, annotation_b, category,
                                annotationmaps, looping_classes, threshold=0,
                                margin=1, asymmetric=False):
    """
    Use Fisher's exact test to compute a one-sided p-value against the null
    hypothesis that the selected loop category's overlap with selected
    annotations across all regions is the same as the special "background"
    reference loop category's overlap with the same annotations.

    Parameters
    ----------
    annotation_a : str
        Annotation to look for on one side of the loop.
    annotation_b : str
        Annotation to look for on the other side of the loop.
    category : str
        The category of loops to consider.
    annotationmaps : dict of annotationmap
        A dict describing the annotations. In total, it should have the
        following structure::

            {
                'annotation_a_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                 },
                'annotation_b_name': {
                    'region_1_name': list of int,
                    'region_2_name': list of int,
                    ...
                },
                ...
            }

        where ``annotationmaps['annotation_a']['region_r']`` should be a list of
        ints describing the number of ``'annotation_a'``s present in each bin of
        ``'region_r'``.
    looping_classes : dict of np.ndarray with str dtype
        The keys should be region names as strings, the values should be square,
        symmetric arrays of the same size and shape as the indicated region,
        with string loop category names in the positions of categorized loops.
    threshold : int
        Bins are defined to contain an annotation if they are "hit" strictly
        more than ``threshold`` times by the annotation.
    margin : int
        A bin is defined to contain an annotation if any bin within ``margin``
        bins is "hit" by the annotation. Corresponds to a "margin for error" in
        the intersection precision.
    asymmetric : bool
        Pass True to only count situations when A is upstream of B. Pass False
        to count intersections regardless of order.

    Returns
    -------
    float
        The p-value.

    Examples
    --------
    >>> import numpy as np
    >>> annotationmaps = {'a': {'r1': [0, 1, 2], 'r2': [1, 0]},
    ...                   'b': {'r1': [1, 1, 0], 'r2': [0, 1]}}
    >>> looping_classes = {'r1': np.array([['npc', ''   , 'es' ],
    ...                                    [''   , ''   , 'npc'],
    ...                                    ['es' , 'npc', ''   ]],
    ...                                   dtype='a25'),
    ...                    'r2': np.array([['ips', 'es' ],
    ...                                    ['es' , ''   ]],
    ...                                   dtype='a25')}
    >>> looping_classes['r1'][looping_classes['r1'] == ''] = 'background'
    >>> looping_classes['r2'][looping_classes['r2'] == ''] = 'background'
    >>> round(get_fisher_exact_pvalue_all('a', 'b', 'es', annotationmaps,
    ...                                   looping_classes, margin=0), 14)
    0.4
    >>> round(get_fisher_exact_pvalue_all('a', 'b', 'npc', annotationmaps,
    ...                                   looping_classes, margin=0), 14)
    0.8
    >>> round(get_fisher_exact_pvalue_all('a', 'b', 'ips', annotationmaps,
    ...                             looping_classes, margin=0), 14)
    0.6
    """
    # count loops in the specified category
    category_loops_total = sum(
        [np.tril(looping_classes[region] == category).sum()
         for region in looping_classes])
    category_loops_hit = count_intersections_all(
        annotation_a, annotation_b, category, annotationmaps, looping_classes,
        threshold=threshold, margin=margin, asymmetric=asymmetric)
    category_loops_not_hit = category_loops_total - category_loops_hit

    # count loops in the background category
    bkgd_loops_total = sum(
        [np.tril(looping_classes[region] == 'background').sum()
         for region in looping_classes])
    bkgd_loops_hit = count_intersections_all(
        annotation_a, annotation_b, 'background', annotationmaps,
        looping_classes, threshold=threshold, margin=margin,
        asymmetric=asymmetric)
    bkgd_loops_not_hit = bkgd_loops_total - bkgd_loops_hit

    # short-circuit if neither category nor background have any hits
    if category_loops_hit == 0 and bkgd_loops_hit == 0:
        return 0.5

    # assemble contingency table
    cont_table = [[category_loops_hit, bkgd_loops_hit],
                  [category_loops_not_hit, bkgd_loops_not_hit]]

    # return the smaller of the two single-tailed p-values
    return min(stats.fisher_exact(cont_table, alternative='less')[1],
               stats.fisher_exact(cont_table, alternative='greater')[1])


def clear_enrichment_caches():
    """
    Clear all caches related to enrichment computations.

    This function is deprecated. Previously, it was necessary to call this
    function within a script whenever the content of ``annotationmaps`` or
    ``looping_classes`` changed. The current cache implementation does not need
    to be cleared when this happens.

    Examples
    --------
    >>> import numpy as np
    >>> clear_enrichment_caches()
    >>> annotationmaps = {'a': {'r1': [0, 0, 2, 1]},
    ...                   'b': {'r1': [1, 1, 0, 0]}}
    >>> looping_classes = {'r1': np.array([[''   , ''   , 'es' , 'ips'],
    ...                                    [''   , ''   , 'npc', 'npc'],
    ...                                    ['es' , 'npc', ''   , ''   ],
    ...                                    ['ips', 'npc', ''   , ''   ]],
    ...                                   dtype='a25')}
    >>> count_intersections('a', 'b', 'r1', 'es', annotationmaps,
    ...                     looping_classes, margin=0)
    1
    >>> looping_classes = {'r1': np.array([[''   , ''   , 'ips', 'ips'],
    ...                                    [''   , ''   , 'npc', 'npc'],
    ...                                    ['ips', 'npc', ''   , ''   ],
    ...                                    ['ips', 'npc', ''   , ''   ]],
    ...                                   dtype='a25')}
    >>> count_intersections('a', 'b', 'r1', 'es', annotationmaps,
    ...                     looping_classes, margin=0)
    0
    >>> clear_enrichment_caches()
    >>> count_intersections('a', 'b', 'r1', 'es', annotationmaps,
    ...                     looping_classes, margin=0)
    0
    """
    process_annotations.cache_clear()
    count_intersections.cache_clear()
    count_intersections_all.cache_clear()
    get_annotation_percentage.cache_clear()
    get_annotation_percentage_all.cache_clear()
    get_fold_change.cache_clear()
    get_fold_change_all.cache_clear()
    get_fisher_exact_pvalue.cache_clear()
    get_fisher_exact_pvalue_all.cache_clear()
