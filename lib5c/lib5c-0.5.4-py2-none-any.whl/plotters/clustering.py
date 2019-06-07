"""
Module for visualizing architectural clusters.
"""

from matplotlib import pyplot as plt

from lib5c.algorithms.clustering.util import clusters_to_array
from lib5c.util.scales import compute_regional_obs_over_exp_scale, \
    compute_track_scales
from lib5c.plotters.heatmap import plot_heatmap
from lib5c.plotters.colorscales import obs_over_exp_colorscale


def compute_bounding_box(cluster_peaks):
    """
    Computes a rectangular bounding box for a cluster.

    Parameters
    ----------
    cluster_peaks : list of dicts of ints
        Each dict in the list represents a peak in the cluster and has the
        form::

            {
                'x': int,
                'y': int
            }

        where these ints represent the respective x- and y-coordinates of the
        peak within the region.

    Returns
    -------
    dict of ints
        The returned dict represents the computed bounding box and has the
        form::

            {
                'x_min': int,
                'x_max': int,
                'y_min': int,
                'y_max': int
            }

        where the ints describe the maximal and minimal indices of pixels along
        the x- and y-axes to be included within the bounding box, respectively.
    """
    return {'x_min': min([peak['x'] for peak in cluster_peaks]),
            'x_max': max([peak['x'] for peak in cluster_peaks]),
            'y_min': min([peak['y'] for peak in cluster_peaks]),
            'y_max': max([peak['y'] for peak in cluster_peaks])}


def make_zoom_window(bounding_box, region_size, padding=2, invert=False):
    """
    Computes a zoom window around a target bounding box.

    Parameters
    ----------
    bounding_box : dict of ints
        This dict represents the target bounding box and should have the form::

            {
                'x_min': int,
                'x_max': int,
                'y_min': int,
                'y_max': int
            }

        where the ints describe the maximal and minimal indices of pixels along
        the x- and y-axes included within the bounding box, respectively.
    region_size : int
        The side length of the square region within which the target bounding
        box lies, in pixels.
    padding : int
        The number of pixels to include within the zoom window around the
        bounding box. If the zoom window is at the edge of the region, it may be
        impossible to pad by the specified number of pixels, in which case the
        zoom window will be shifted away from the edge of the region.
    invert : bool
        If True, the zoom window will be reflected across the diagonal.

    Returns
    -------
    dict of int
        This dict represents the computed zoom window and has the following
        structure::

            {
                'x_start': int,
                'y_start': int,
                'size': int
            }

        where x_start and y_start refer to the indices of the lowest-indexed
        pixel to be included in the zoom window along each axis, and size
        indicates the side length of the square zoom window in pixels.
    """
    # figure out how large the window should be
    zoom_window_size = max(
        bounding_box['x_max'] - bounding_box['x_min'],
        bounding_box['y_max'] - bounding_box['y_min']) + 1 + 2 * padding

    # make a first guess at where the window should be
    zoom_window = {'x_start': bounding_box['x_min'] - padding,
                   'y_start': bounding_box['y_min'] - padding,
                   'size': zoom_window_size}
    if invert:
        zoom_window = {'x_start': bounding_box['y_min'] - padding,
                       'y_start': bounding_box['x_min'] - padding,
                       'size': zoom_window_size}

    # shift the window if we're close to the edge of the heatmap
    if zoom_window['x_start'] + zoom_window['size'] - 1 >= region_size:
        zoom_window['x_start'] -= zoom_window['x_start'] + zoom_window['size'] \
            - region_size
    if zoom_window['y_start'] + zoom_window['size'] - 1 >= region_size:
        zoom_window['y_start'] -= zoom_window['y_start'] + zoom_window['size'] \
            - region_size
    if zoom_window['x_start'] < 0:
        zoom_window['x_start'] -= zoom_window['x_start']
    if zoom_window['y_start'] < 0:
        zoom_window['y_start'] -= zoom_window['y_start']

    return zoom_window


def plot_cluster(pixelmap, counts_superdict, cluster_peaks, cluster_region,
                 colorscales='auto', tracks=(),
                 track_filename_generator=lambda x: '%s.bed' % x, conditions=(),
                 track_scales='auto', zoom_window='auto', padding=2,
                 invert=False,
                 output_filename_generator=lambda x, y: 'output/%s_%s' % (x, y),
                 heatmap_kwargs='default'):
    """
    Plots a contact probability heatmaps centered on a cluster.

    Parameters
    ----------
    pixelmap : pixelmap
        The pixelmap to use for plotting the heatmap. See
        ``lib5c.parsers.bed.get_pixelmap()``.
    counts_superdict : dict of counts dicts
        The contact probability data for each replicate to be plotted. The keys
        of the outer dict are replicate names as strings. The values of the
        outer dict are counts dicts whose keys are region names as strings and
        whose values are 2D square symmetric numpy arrays containing the counts
        for that region in that replicate. See ``lib5c.util.counts_superdict``.
    cluster_peaks : list of dicts of ints
        Each dict in the list represents a peak in the cluster and has the
        form::

            {
                'x': int,
                'y': int
            }

        where these ints represent the respective x- and y-coordinates of the
        peak within the region.
    cluster_region : str
        The name of the region in which the cluster lies.
    colorscales : 'auto' or dict of lists of numerics
        If 'auto' is passed, the regional colorscales for the heatmaps are
        automatically computed using
        ``lib5c.util.scales.compute_regional_obs_over_exp_scale()``.
        Alternatively, the colorscales may be specified as a dict
        whose keys are region names and whose values are lists of numerics of
        length two. The first element of this list will be the minumum value on
        the colorscale, while the second element will be the maximum value on
        the colorscale.
    tracks : list of str
        List of string identifiers for ChIP-seq tracks to include on the
        heatmaps. The identifiers will be used to find the appropriate BED files
        on the disk according to track_filename_generator.
    track_filename_generator : function str -> str
        When passed any string from tracks, this function should return a string
        reference to the BED file on the disk containing the BED features for
        that track.
    conditions : list of str
        List of string identifiers for distinct conditions in the dataset. If
        this list is not empty, it will be used to group replicates and tracks
        into distinct groups that contain the identifiers in this list as
        substrings of their names. Replicates identified as belonging to a
        certain condition will be plotted with the tracks identified as
        belonging to that same condition. For example, consider a conditions
        list ['ES', 'NPC'], replicates 'NPC_Rep1' and 'ES_Rep1', and tracks
        'ES_CTCF' and 'NPC_CTCF'. The 'ES_Rep1' heatmap will be drawn with the
        'ES_CTCF' track, and the 'NPC_Rep1' heatmap will be drawn with the
        'NPC_CTCF' track. If this list is empty, all tracks will be drawn with
        all heatmaps. Additionally, this kwarg is included in the call to
        ``lib5c.util.scales.compute_track_scales()``, which computes the track
        scales if track_scales is 'auto' (see below).
    track_scales : 'auto' or dict of numerics
        If 'auto' is passed, the track scales will be computed automatically
        using ``lib5c.util.scales.compute_track_scales()``. The conditions kwarg
        will be included in this call. For example, consider a conditions list
        ['ES', 'NPC'], and tracks 'ES_CTCF' and 'NPC_CTCF'. Since the track
        names differ only in their condition identifier, these two tracks will
        be plotted using the same scale if track_scales is 'auto'.
        Alternatively, the track scales may be specified as a dict whose keys
        are the track names and whose values are numerics specifying the maximum
        value of the scale for that track. The minumum value of all tracks is
        assumed to be zero.
    zoom_window : 'auto' or dict of int
        If 'auto' is passed, a zoom window for the cluster will be automatically
        computed. Alternatively, the zoom window may be specified as a dict with
        the following structure::

            {
                'x_start': int,
                'y_start': int,
                'size': int
            }

        where x_start and y_start refer to the indices of the lowest-indexed
        pixel to be included in the zoom window along each axis, and size
        indicates the side length of the square zoom window in pixels.
    padding : int
        If zoom_window is 'auto', this kwarg specifies how much padding to
        include around the cluster boundaries when computing the zoom window.
    invert : bool
        If zoom_window is 'auto', this kwarg specifies whether or not the
        automatically computed zoom window should be reflected across the
        diagonal, reversing the x- and y-axes on the resulting heatmaps.
    output_filename_generator : function (str, str) -> str
        This function should take in cluster_region and the name of a replicate
        and return the output filename to write the corresponding heatmap to.
    heatmap_kwargs : 'default' or dict
        Passing a dict to this kwarg allows the specification of arbitrary
        kwargs to be included in the final call to
        ``lib5c.plotters.heatmap.plot_heatmap()``. If 'default' is passed
        instead of a dict, a default dict of typical kwargs will be used.
    """
    # auto zoom window
    if zoom_window == 'auto':
        zoom_window = make_zoom_window(compute_bounding_box(cluster_peaks),
                                       len(pixelmap[cluster_region]), padding,
                                       invert=invert)

    # auto colorscales
    if colorscales == 'auto':
        colorscales = {
            region: compute_regional_obs_over_exp_scale(counts_superdict,
                                                        region)
            for region in pixelmap.keys()}

    # auto track scales
    if track_scales == 'auto':
        track_scales = compute_track_scales(tracks, pixelmap, conditions,
                                            track_filename_generator)

    # compute replicates by condition
    if conditions:
        replicates_by_condition = {
            condition: [replicate for replicate in counts_superdict.keys()
                        if condition in replicate]
            for condition in conditions
        }
    else:
        replicates_by_condition = {
            'any': [replicate for replicate in counts_superdict.keys()]
        }

    # compute tracks by condition
    if conditions:
        tracks_by_condition = {
            condition: [track for track in tracks if condition in track]
            for condition in conditions
        }
    else:
        tracks_by_condition = {'any': [track for track in tracks]}

    # sane defaults for heatmap_kwargs
    if heatmap_kwargs == 'default':
        heatmap_kwargs = {'show_colorscale': False,
                          'cmap': obs_over_exp_colorscale,
                          'cluster_colors': 'lime'}

    for condition in replicates_by_condition.keys():
        for rep in replicates_by_condition[condition]:
            plot_heatmap(
                counts_superdict[rep][cluster_region],
                output_filename_generator(cluster_region, rep),
                region=cluster_region,
                pixelmap=pixelmap,
                zoom_window=zoom_window,
                colorscale=colorscales[cluster_region],
                tracks=[track_filename_generator(track)
                        for track in tracks_by_condition[condition]],
                track_scales=[track_scales[track][cluster_region]
                              for track in tracks_by_condition[condition]],
                clusters=[cluster_peaks],
                **heatmap_kwargs
            )


def plot_cluster_indices(pixelmap, clusters,
                         output_filename_generator=lambda x: '%s_indices' % x,
                         heatmap_kwargs='default'):
    """
    Plots clusters for each region where each cluster is in a different color
    and each cluster is labeled with its index in the list of clusters for that
    region.

    Parameters
    ----------
    pixelmap : pixelmap
        The pixelmap to use for plotting the heatmap. See
        ``lib5c.parsers.bed.get_pixelmap()``.
    clusters : dict of lists of lists of dicts of ints
        The keys of the outer dict are region names. The values (the outer
        lists) represent the list of clusters within each region. The inner
        lists represent clusters. Each dict in each inner list represents a peak
        in that cluster and has the form::

            {
                'x': int,
                'y': int
            }

        where these ints represent the respective x- and y-coordinates of the
        peak within the region. As an example, we should be able to index into
        clusters as follows::

            clusters[region_name : str][index of cluster within region : int]\
                    [index of peak within cluster : int] = \
                {
                    'x': int,
                    'y': int
                }

    output_filename_generator : function str -> str
        This function should take in a region name and return the output
        filename to which the cluster index heatmap for that region should be
        written.
    heatmap_kwargs : 'default' or dict
        Passing a dict to this kwarg allows the specification of arbitrary
        kwargs to be included in the final call to
        ``lib5c.plotters.heatmap.plot_heatmap()``. If 'default' is passed
        instead of a dict, a default dict of typical kwargs will be used.
    """
    # deduce regions
    regions = pixelmap.keys()

    # sane defaults for heatmap_kwargs
    if heatmap_kwargs == 'default':
        heatmap_kwargs = {'show_colorscale': False,
                          'cmap': plt.get_cmap('gist_ncar')}

    # plot heatmaps
    for region in regions:
        plot_heatmap(clusters_to_array(clusters[region], len(pixelmap[region])),
                     output_filename_generator(region),
                     pixelmap=pixelmap,
                     region=region,
                     clusters=clusters[region],
                     cluster_labels='indices',
                     **heatmap_kwargs)


# test client
def main():
    import pickle

    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts

    # hardcode replicates
    replicates = ['ES_Rep1',
                  'NPC_Rep31']

    # hardcode conditions
    conditions = ['ES', 'NPC']

    # hardcode tracktypes
    tracktypes = ['Smc1', 'CTCF', 'H3K4me1', 'H3K27ac']

    # compute tracks
    tracks = ['%s_%s' % (tracktype, condition)
              for tracktype in tracktypes
              for condition in conditions]

    # get pixelmap
    pixelmap = load_primermap('test/bins_nuc.bed')

    # load counts
    counts_superdict = {
        replicate: load_counts('test/%s_obs_over_exp.counts' % replicate)
        for replicate in replicates}

    # a set of clusters
    with open('test/clusters.pickle', 'rb') as handle:
        clusters = pickle.load(handle)

    # plot cluster indices
    plot_cluster_indices(
        pixelmap, clusters,
        output_filename_generator=lambda x: 'test/clusters/%s_indices' % x)

    # plot zoomin heatmaps
    plot_cluster(
        pixelmap, counts_superdict, clusters['Klf4'][1], 'Klf4',
        colorscales='auto', tracks=tracks,
        track_filename_generator=lambda x: 'test/tracks/%s.bed' % x,
        conditions=conditions, track_scales='auto', zoom_window='auto',
        padding=2, invert=False,
        output_filename_generator=lambda x, y: 'test/clusters/%s_%s' %
                                               (x, y),
        heatmap_kwargs={'show_colorscale': True,
                        'cmap'           : obs_over_exp_colorscale,
                        'cluster_colors' : 'pink'}
    )


if __name__ == "__main__":
    main()
