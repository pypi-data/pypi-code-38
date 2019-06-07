import numpy as np
from scipy.ndimage import label, generate_binary_structure
from sklearn.metrics import confusion_matrix

from lib5c.util.parallelization import parallelize_regions
from lib5c.structures.dataset import Dataset
from lib5c.util.metrics import cohens_kappa
from lib5c.util.statistics import adjust_pvalues, stouffer, convert_to_two_tail


def two_way_thresholding(pvalues_superdict, primermap, conditions=None,
                         significance_threshold=1e-15, bh_fdr=False,
                         two_tail=False, concordant=False,
                         distance_threshold=24000, size_threshold=3,
                         background_threshold=0.6, report_clusters=True):
    """
    All-in-one heavy-lifting function for thresholding.

    Parameters
    ----------
    pvalues_superdict : dict of dict of np.ndarray
        The p-values to threshold.
    primermap : primermap
        The primermap associated with the pvalues_superdict.
    conditions : list of str, optional
        The list of condition names. Pass None to skip condition comparisons.
    significance_threshold : float
        The p-value or q-value to threshold significance with.
    bh_fdr : bool
        Pass True to apply multiple testing correction (BH-FDR) before checking
        the ``significance_threshold``.
    two_tail : bool
        If ``bh_fdr=True``, pass True here to perform the BH-FDR on two-tailed
        p-values, but only report the significant right-tail events as loops.
        Note that two-tailed p-values are only accurate if p-values were called
        using a continuous distribution.
    concordant : bool
        Pass True to report only those interactions which are significant in all
        replicates in each condition. Pass False to combine evidence from all
        replicates within each condition instead.
    distance_threshold : int
        Interactions with interaction distance (in bp) shorter than this will
        not be called.
    size_threshold : int
        Interactions within connected components smaller than this will not be
        called.
    background_threshold : float, optional
        The p-value threshold to use to call a background loop class. Pass None
        to skip calling a background class.
    report_clusters : bool
        Pass True to perform a second pass of connected component counting at
        the very end, reporting the numbers of clusters in each color category
        to the returned Dataset.

    Returns
    -------
    Dataset
        The results of the thresholding.
    """
    # resolve conditions
    if conditions is None:
        conditions = ['dummy_condition']

    # prepare dataset
    print 'preparing dataset'
    d = Dataset.from_counts_superdict(
        pvalues_superdict,
        primermap,
        name='rep_pvalue',
        repinfo=conditions
    )
    d.dropna(name='rep_pvalue')

    # distance thresholding
    print 'distance thresholding'
    filter_near_diagonal(d.df, distance=distance_threshold)

    # combine replicate information per condition
    for cond in d.conditions:
        d.df[('pvalue', cond)] = stouffer(
            d.df[[('rep_pvalue', rep) for rep in d.cond_reps[cond]]],
            axis=1
        )

    # significance threhsolding
    print 'significance thresholding'
    threshold_column = 'pvalue'
    if bh_fdr:
        if two_tail:
            d.apply_per_replicate(
                convert_to_two_tail, 'pvalue', 'two_tail_pvalue')
            d.apply_per_replicate(
                convert_to_two_tail, 'rep_pvalue', 'rep_two_tail_pvalue')
            d.apply_per_replicate(
                adjust_pvalues, 'two_tail_pvalue', 'two_tail_qvalue')
            d.apply_per_replicate(
                adjust_pvalues, 'rep_two_tail_pvalue', 'rep_two_tail_qvalue')
            d.apply_per_replicate(
                lambda x, y: np.where(y < 0.5, x, 1.0),
                ['two_tail_qvalue', 'pvalue'], 'qvalue')
            d.apply_per_replicate(
                lambda x, y: np.where(y < 0.5, x, 1.0),
                ['rep_two_tail_qvalue', 'rep_pvalue'], 'rep_qvalue')
        else:
            d.apply_per_replicate(adjust_pvalues, 'pvalue', 'qvalue')
            d.apply_per_replicate(adjust_pvalues, 'rep_pvalue', 'rep_qvalue')
        threshold_column = 'qvalue'
    d.apply_per_replicate(
        lambda x: x < significance_threshold, threshold_column,
        'significant_unfiltered')
    d.apply_per_replicate(
        lambda x: x < significance_threshold, 'rep_%s' % threshold_column,
        'rep_significant_unfiltered')

    # cluster size filtering
    if size_threshold > 1:
        print 'size thresholding'
        if not concordant:
            d.add_columns_from_counts_superdict(
                {cond: size_filter(
                    d.counts(name='significant_unfiltered', rep=cond),
                    size_threshold)
                 for cond in d.conditions},
                'significant',
                rep_order=d.conditions
            )
        else:
            d.add_columns_from_counts_superdict(
                {rep: size_filter(
                    d.counts(name='rep_significant_unfiltered', rep=rep),
                    size_threshold)
                 for rep in d.reps},
                'rep_significant',
                rep_order=d.reps
            )
    else:
        if not concordant:
            d.apply_per_replicate(lambda x: x, 'significant_unfiltered',
                                  'significant')
        else:
            d.apply_per_replicate(lambda x: x, 'rep_significant_unfiltered',
                                  'rep_significant')

    # concordance within conditions
    if concordant:
        print 'computing concordance within conditions'
        for cond in d.conditions:
            d.df['concordant', cond] = np.all(
                [d.df.loc[:, ('rep_significant', rep)].as_matrix()
                 for rep in d.cond_reps[cond]], axis=0)

    # intersections across conditions
    if len(d.conditions) == 2:
        print 'intersecting across conditions'
        criterion = 'concordant' if concordant else 'significant'
        d.df['color'] = ''
        d.df.loc[d.df[criterion, d.conditions[0]] &
                 d.df[criterion, d.conditions[1]], 'color'] \
            = 'constitutive'
        d.df.loc[d.df[criterion, d.conditions[0]] &
                 ~d.df[criterion, d.conditions[1]], 'color'] \
            = '%s_only' % d.conditions[0]
        d.df.loc[~d.df[criterion, d.conditions[0]] &
                 d.df[criterion, d.conditions[1]], 'color'] \
            = '%s_only' % d.conditions[1]

    # add background
    if background_threshold is not None:
        print 'adding background'
        d.df.loc[np.all(d.df['rep_pvalue'].as_matrix() > background_threshold,
                        axis=1),
                 'color'] = 'background'

    # report cluster info
    if report_clusters is True:
        print 'counting final clusters'
        color_counts = d.counts('color')
        for color in set(d.df['color'].unique()) - {'background', ''}:
            d.add_column_from_counts(
                label_connected_components(color_counts, color), color)

    return d


def kappa(d):
    """
    Compute the Cohen's kappa values between the replicates of each condition.

    Parameters
    ----------
    d : Dataset
        Dataset processed by `two_way_thresholding()`.

    Returns
    -------
    dict
        The keys are condition names, the values are the kappa values.
    """
    key = 'rep_significant' if ('rep_significant', d.reps[0]) in d.df.columns \
        else 'rep_significant_unfiltered'
    return {cond: cohens_kappa(*[d.df.loc[:, (key, rep)]
                                 for rep in d.cond_reps[cond]])
            for cond in d.conditions}


def concordance_confusion(d):
    """
    Extract the within-condition concordance confusion matrices.

    Parameters
    ----------
    d : Dataset
        Dataset processed by `two_way_thresholding()`.

    Returns
    -------
    dict
        The keys are condition names, the values are the 2x2 confusion matrices.
    """
    key = 'rep_significant' if ('rep_significant', d.reps[0]) in d.df.columns \
        else 'rep_significant_unfiltered'
    return {cond: confusion_matrix(*[d.df.loc[:, (key, rep)]
                                     for rep in d.cond_reps[cond]])
            for cond in d.conditions}


def color_confusion(d):
    """
    Extract the across-condition color confusion matrix.

    Parameters
    ----------
    d : Dataset
        Dataset processed by `two_way_thresholding()`.

    Returns
    -------
    np.ndarray
        The 2x2 confusion matrix.
    """
    criterion = 'concordant' if 'concordant' in {c[0] for c in list(d.df)} \
        else 'significant'
    return confusion_matrix(*[d.df.loc[:, (criterion, cond)]
                              for cond in d.conditions])


def count_clusters(d):
    """
    Extract the final cluster counts.

    Parameters
    ----------
    d : Dataset
        Dataset processed by `two_way_thresholding()` called with
        `report_clusters=True`.

    Returns
    -------
    dict
        The keys are the color names as strings, the values are integers
        representing the cluster counts.
    """
    cluster_counts = {}
    for color in set(d.df['color'].unique()) - {'background', ''}:
        if not type(color) == str:
            continue
        row_idx = d.df[color] != 0
        cluster_counts[color] = len(
            np.unique(d.df.loc[row_idx, color].map(str) + '_' +
                      d.df.loc[row_idx, 'region']))
    return cluster_counts


def filter_near_diagonal(df, distance=24000, drop=True):
    """
    Drops rows from df where its 'distance' column is less than k.

    Dropping occurs in-place.

    Parameters
    ----------
    df : pd.DataFrame
        Must have a 'distance' column.
    distance : int
        Threshold for distance (in bp).
    drop : bool
        Pass True to drop the filtered rows in-place. Pass False to return an
        index subset for the filtered rows instead.
    """
    index_subset = (df[df['distance'] < distance]).index
    if drop:
        df.drop(index_subset, inplace=True)
    else:
        return index_subset


@parallelize_regions
def size_filter(calls, threshold):
    """
    Removes calls which are in connected components smaller than a threshold.

    Parameters
    ----------
    calls : np.ndarray
        Boolean matrix of calls.
    threshold : int
        Connected components smaller than this will be removed.

    Returns
    -------
    np.ndarray
        The filtered calls.

    Examples
    --------
    >>> calls = np.array([[ True,  True, False,  True],
    ...                   [ True,  True, False, False],
    ...                   [False, False, False,  True],
    ...                   [ True, False,  True,  True]])
    >>> size_filter(calls, 3)
    array([[ True,  True, False, False],
           [ True,  True, False, False],
           [False, False, False, False],
           [False, False, False, False]])
    """
    components, num_components = label(
        np.tril(calls), structure=generate_binary_structure(2, 2))
    for i in range(1, num_components + 1):
        if np.sum(components == i) < threshold:
            components[components == i] = 0
    result = components > 0
    return result | result.T


@parallelize_regions
def label_connected_components(colors, color):
    """
    Labels the connected components of a specific loop color.

    Parameters
    ----------
    colors : np.ndarray with string dtype
        The matrix of colors.
    color : str
        The color to label.

    Returns
    -------
    np.ndarray
        Same size and shape as colors, entries are ints which are the labels

    Examples
    --------
    >>> colors = np.array([['a', 'a', 'b', 'a'],
    ...                    ['a', 'a', 'b', 'b'],
    ...                    ['b', 'b', 'b', 'a'],
    ...                    ['a', 'b', 'a', 'a']])
    >>> print(label_connected_components(colors, 'a'))
    [[1 1 0 2]
     [1 1 0 0]
     [0 0 0 3]
     [2 0 3 3]]
    """
    calls = colors == color
    components, _ = label(
        np.tril(calls), structure=generate_binary_structure(2, 2))
    return components | components.T
