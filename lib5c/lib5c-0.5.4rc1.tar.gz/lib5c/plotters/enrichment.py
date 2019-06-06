"""
Module for plotting visualizations of enrichments of annotations within
categories of categorized loops.
"""

from __future__ import division

import numpy as np
from matplotlib import pyplot as plt

from lib5c.algorithms.enrichment import get_annotation_percentage_all, \
    get_fisher_exact_pvalue_all
from lib5c.util.plotting import plotter


@plotter
def plot_looptype_vs_annotation_heatmap(annotationmaps, looping_classes,
                                        constant_annotation,
                                        loop_type_order=None,
                                        annotation_order=None, threshold=0,
                                        margin=1, vmin=-2.0, vmax=2.0,
                                        despine=False, style='dark', **kwargs):
    """
    Plot a heatmap of enrichments for one fixed annotation, varying the loop
    category on the x-axis and the annotation on the other side on the y-axis.

    Parameters
    ----------
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
    constant_annotation : str
        The annotation to hold constant throughout the heatmap.
    loop_type_order : list of str
        The loop categories to include on the x-axis, in order. If None, falls
        back to the sorted unique categories in ``looping_classes``.
    annotation_order : list of str, optional
        The annotations to include on the y-axis, in order. If None, falls back
        to ``sorted(annotationmap.keys())``.
    threshold : int
        Bins are defined to contain an annotation if they are "hit" strictly
        more than ``threshold`` times by the annotation.
    margin : int
        A bin is defined to contain an annotation if any bin within ``margin``
        bins is "hit" by the annotation. Corresponds to a "margin for error" in
        the intersection precision.
    vmin : float
        The lowest fold change to show on the colorbar.
    vmax : float
        The highest fold change to show on the colorbar.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    # resolve looping_classes
    if loop_type_order is None:
        loop_type_order = sorted(set(np.unique(np.concatenate(
            [looping_classes[region].flatten()
             for region in looping_classes]))) - {'', 'background'})

    # resolve annotation_order
    if annotation_order is None:
        annotation_order = sorted(annotationmaps.keys())

    # prepare array for imshow
    array = []
    for i in range(len(annotation_order)):
        row = []
        for j in range(len(loop_type_order)):
            selected_dict = get_annotation_percentage_all(
                annotation_order[i], constant_annotation, loop_type_order[j],
                annotationmaps, looping_classes, threshold=threshold,
                margin=margin)
            background_dict = get_annotation_percentage_all(
                annotation_order[i], constant_annotation, 'background',
                annotationmaps, looping_classes, threshold=threshold,
                margin=margin)

            if background_dict:
                fold_enrichment = selected_dict / float(background_dict)
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
            selected_dict = get_fisher_exact_pvalue_all(
                annotation_order[i], constant_annotation, loop_type_order[j],
                annotationmaps, looping_classes, threshold=threshold,
                margin=margin)
            row.append(selected_dict)
        p_values.append(row)

    # plot heatmap
    fig = plt.gcf()
    fig.set_size_inches(72 / 60.0 * len(annotation_order),
                        40 / 60.0 * len(annotation_order))
    cmap = plt.get_cmap('bwr')
    im = plt.imshow(array, interpolation='none', cmap=cmap, origin='lower',
                    vmin=vmin, vmax=vmax)
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
            elif p_values[i][j] == 0.0:
                text = '0.0'
            else:
                text = 'E-%i' % int(-np.log10(p_values[i][j]))
            plt.text(j, i, text, ha='center', va='center')
    plt.colorbar(im)
    plt.xticks(np.arange(len(loop_type_order)), loop_type_order, rotation=45,
               ha='right')
    plt.yticks(np.arange(len(annotation_order)), annotation_order)


@plotter
def plot_annotation_vs_annotation_heatmap(annotationmaps, looping_classes,
                                          loop_type, axis_order=None,
                                          threshold=0, margin=1, vmin=-2.0,
                                          vmax=2.0, despine=False, style='dark',
                                          **kwargs):
    """
    Plot a heatmap of enrichments for a fixed loop category, varying the
    annotation on either side on the x- and y-axes.

    Parameters
    ----------
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
    loop_type : str
        The loop category to hold constant throughout the heatmap.
    axis_order : list of str, optional
        The annotations to include on each axis, in order. If None, falls back
        to ``sorted(annotationmap.keys())``.
    threshold : int
        Bins are defined to contain an annotation if they are "hit" strictly
        more than ``threshold`` times by the annotation.
    margin : int
        A bin is defined to contain an annotation if any bin within ``margin``
        bins is "hit" by the annotation. Corresponds to a "margin for error" in
        the intersection precision.
    vmin : float
        The lowest fold change to show on the colorbar.
    vmax : float
        The highest fold change to show on the colorbar.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    # resolve axis_order
    if axis_order is None:
        axis_order = sorted(annotationmaps.keys())

    # prepare fold change array
    array = []
    for i in range(len(axis_order)):
        row = []
        for j in range(len(axis_order)):
            selected_dict = get_annotation_percentage_all(
                axis_order[i], axis_order[j], loop_type, annotationmaps,
                looping_classes, threshold=threshold, margin=margin)
            background_dict = get_annotation_percentage_all(
                axis_order[i], axis_order[j], 'background', annotationmaps,
                looping_classes, threshold=threshold, margin=margin)
            if background_dict:
                fold_enrichment = selected_dict / background_dict
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
            selected_dict = get_fisher_exact_pvalue_all(
                axis_order[i], axis_order[j], loop_type, annotationmaps,
                looping_classes, threshold=threshold, margin=margin)
            row.append(selected_dict)
        p_values.append(row)

    # plot heatmap
    fig = plt.gcf()
    fig.set_size_inches(72 / 60.0 * len(axis_order),
                        40 / 60.0 * len(axis_order))
    cmap = plt.get_cmap('bwr')
    im = plt.imshow(array, interpolation='none', cmap=cmap, origin='lower',
                    vmin=vmin, vmax=vmax)
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
            elif p_values[i][j] == 0.0:
                text = '0.0'
            else:
                text = 'E-%i' % int(-np.log10(p_values[i][j]))
            plt.text(j, i, text, ha='center', va='center')
    plt.colorbar(im)
    plt.xticks(np.arange(len(axis_order)), axis_order, rotation=45, ha='right')
    plt.yticks(np.arange(len(axis_order)), axis_order)


@plotter
def plot_stack_bargraph(annotation_a, annotation_b, loop_types, labels, colors,
                        annotationmaps, looping_classes, threshold=0, margin=1,
                        **kwargs):

    """
    Plots a bar graph with loop types arranged on the x-axis and the percentage
    of times ``annotation_a`` is interaction with ``annotation_b`` in all the
    loops of that loop type.

    Parameters
    ----------
    annotation_a : str
        First annotation you are intereted in.
    annotation_b : str
        Second annotation you are interested in.
    loop_types : list of str
        The order in which to arrange the loop types along the x-axis, from left
        to right. If you exclude a loop type from this list, it will be excluded
        from the heatmap.
    labels : list of str
        The labels you want to be assigned on the x-axis to each of the loop
        types. The label order should correspond to the order of ``loop_types``.
    colors : list of valid matplotlib colors
        The colors to plot each bar with. The order should correspond to the
        order of ``loop_types``.
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
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    # extract data
    array_data = [100 * get_annotation_percentage_all(
        annotation_a, annotation_b, loop_type, annotationmaps,
        looping_classes,
        threshold=threshold, margin=margin) for loop_type in loop_types]

    # plot figure
    plt.clf()
    plt.figure(num=None, figsize=(5, 3.5), dpi=200, facecolor='w',
               edgecolor='w')
    xlocations = np.array(range(len(array_data))) + 0.5
    width = 0.5
    plt.axhline(y=array_data[len(loop_types) - 1], linestyle='--',
                linewidth=3.0,
                color='#666666')
    plt.bar(xlocations, array_data, width=width, color=colors)
    plt.xticks(xlocations + width / 2, labels, fontsize=6)
    plt.xlim(0, xlocations[-1] + width * 2)
    plt.ylabel(
        'Percentage with %s against %s' % (annotation_a, annotation_b),
        fontsize=5)
