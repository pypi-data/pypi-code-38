"""
Module for plotting 5C heatmaps.
"""

import os
import numbers
import warnings
import subprocess
import uuid
from copy import deepcopy

import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import cm as cm
from matplotlib.gridspec import GridSpec

from lib5c.parsers.bed import load_features
from lib5c.parsers.primers import load_primermap
from lib5c.parsers.genes import load_genes
from lib5c.util.counts import flatten_regional_counts
from lib5c.util.parallelization import parallelize_regions
from lib5c.plotters.colormaps import get_colormap


@parallelize_regions
def plot_heatmap(array, outfile, tracks=(), colorscale=None,
                 show_colorscale=True, cmap='obs', relative_height=0.1,
                 region=None, pixelmap=None, regional_pixelmap=None,
                 primer_file=None, gene_track='mm9', normalize=False,
                 track_scales="auto-each", track_scales_scalar=1.0,
                 zoom_window=None, show_track_labels=True, clusters=None,
                 cluster_colors=None, outline_color=None, cluster_weight="100x",
                 outline_weight=2, cluster_labels=None, segmentation=None,
                 segmentation_colors='auto', communities=None,
                 chipseq_track_line_width=0.1):
    """
    Plots a heatmap with optional colorscale, ChIP-seq tracks, and cluster
    outlining.

    Parameters
    ----------
    array : 2D square numpy array
        The values to plot in the heatmap.
    outfile : str
        String reference to the file to write the heatmap image to. If you
        don't specify an extension, .png will be appended.
    tracks : list of str
        List of string references to .bed files containing ChIP-seq peaks to
        plot with the heatmap. The maximum number of tracks that can be added is
        four. If the bigWigToBedGraph utility is available, you can pass bigwig
        files here instead (with extension .bw).
    colorscale : list of two numbers
        Describes the min and max of the colorscale. Also used as the kwargs
        vmin and vmax in the call to imshow, providing a means to automatically
        normalize the heatmap values. By default, this is set to the min and the
        max of the data.
    show_colorscale : boolean
        If True, add a colorbar to the right of the heatmap.
    cmap : instance of matplotlib.colors.Colormap or str
        The colormap with which to plot the heatmap, or a string that can be
        resolved by ``lib5c.plotters.colormaps.get_colormap()``.
    relative_height : float
        The relative height of the ChIP-seq tracks as a fraction of the heatmap
        height. Ignored if no ChIP-seq tracks are being plotted.
    region : str
        The string name of the region shown in the heatmap. This kwarg is not
        required if regional_pixelmap is passed.
    pixelmap : dict of lists of dicts
        The keys of the outer dict are region names. The values are lists, where
        the ith entry represents the ith bin in that region. Bins are
        represented as dicts with at least the following structure::

            {
                'chrom': str,
                'start': int,
                'end'  : int
            }

        See ``lib5c.parsers.primers.get_pixelmap()``.
    regional_pixelmap : lists of dicts
        Instead of passing a complete pixelmap, you may pass the regional
        pixelmap for just this region.
    primer_file : str
        For backwards compatibility, you can pass a string reference to a bin
        bedfile instead as this kwarg instead of passing pixelmap, and that
        bedfile will be used to create a pixelmap using
        ``lib5c.parsers.primers.get_pixelmap()`` using the default bin name
        parser. It is recommended to pass ``pixelmap`` instead. This kwarg will
        be ignored if pixelmap is passed.
    gene_track : str
        Information about what gene track to plot. Pass a reference to a BED6
        file to load information from that file. %%c in the reference will be
        replaced with the chromosome name. Pass 'mm9' to use the built-in gene
        tracks for mm9.
    normalize : bool
        If True, the heatmap will be normalized by subtracting the minimum and
        dividing by the maximum for the values in the array before plotting.
    track_scales : many types accepted
        This kwarg controls how the heights of the bars in the ChIP-seq tracks
        are scaled. The behavior depends on what is passed in this kwarg. The
        options are as follows::

            single numeric : set the max height of all tracks to this number
            list of numerics, length equal to number of tracks: set the height
                of the ith chipseq track to the ith element of this list
            list of numerics, length equal to number of tracks / 2: set the
                height of the ith pair of tracks to the ith element
            "auto-each": set the max height of each track to its max value in
                the window
            "auto-all": set the max height of all tracks to the max value seen
                across all tracks
            "auto-pairs": set the max height of both tracks in each pair to the
                max value seen across both tracks in the pair

    track_scales_scalar : float
        The values computed according to the track_scales kwarg will be
        multiplied by this value. This enables zooming the y-axis of all the
        ChIP-seq tracks in or out by the same fractional value.
    zoom_window : dict or tuple or None
        If this kwarg is None, the entire selected region will be plotted. To
        zoom the heatmap, you may pass a dict with the following structure::

            {
                'x_start' : int,
                'y_start' : int,
                'size'    : int
            }

        where x_start is the index of the first bin to include on the x-axis,
        y_start is the index of the first bin to include on the y-axis, and size
        is the number of bins to include in the zoom window along both axes.
        Alternatively, you can pass a tuple of the form::

            ('chr3:34459302-34576915', 'chr3:34459302-34576915')

        where the first and the second elements are string representations of
        the genomic ranges to be zoomed to on the x- and y-axes, respectively.
    show_track_labels : bool
        If True, the name of the bed file passed in tracks will be drawn over
        the relevant ChIP-seq track as a label. If False, this will be omitted.
    clusters : list of lists of dicts
        A list of clusters to outline on the heatmap. Each element in the outer
        list is a cluster, and each element in the inner list is a pixel in that
        cluster, represented as a dict with at least the following keys::

            {
                'x': int,
                'y': int
            }

    cluster_colors : many types accepted
        This kwarg controls the colors the clusters will be drawn with. The
        behavior depends on what is passed in this kwarg. The options are as
        follows::

            "random" : colors will be automatically assigned to the clusters
                using a rapidly diverging colorsale
            valid matplotlib color : all clusters will be assigned this color
            list of valid matplotlib colors : cluster colors will be taken from
                this list in order
            None : clusters will not be outlined

    outline_color : valid matplotlib color
        A valid matplotlib color to use to outline the cluster outlines with.
    cluster_weight : numeric or str
        The line width to use for drawing the clusters. Pass a string ending in
        "x" (such as "100x") to specify the line width as a multiple of the
        inverse of the number of pixels in the heatmap. Pass a numeric to send
        the value of this kwarrg to matplotlib, ignoring the size of the
        heatmap.
    outline_weight : numeric or str
        How much wider the outline outline should be than the cluster linewidth.
        Pass a string ending in "x" (such as "2x") to specify the line width as
        a mutlpile of the cluster linewidth. Pass a numeric to make the outline
        linewidth that much thicker than the cluster linewidth in absolute
        matplotlib units. This kwarg is ignored if clusters is None or if
        outline_color is None.
    cluster_labels : many types accepted
        This kwarg allows annotations to be plotted for each cluster at the
        center of mass of the cluster. If a list of strings is passed with the
        same length as clusters, the ith string in the list will be written at
        the center of mass of the ith cluster. You can pass the string literal
        "indices" to write the indices of the clusters. This is equivalent to
        passing range(len(clusters)). If you don't want anything written on your
        clusters, pass None. This kwarg is ignored if clusters is None.
    segmentation : features
        A genome segmentation in the form of a nested dict. The keys to the
        outer dict should be chromosome names as strings. The values of the dict
        should be lists of dicts representing the features on that chromosome
        and should have the following structure::

            {
                'chrom': str,
                'start': int,
                'end': int,
                'id': str
            }

        Where id is a string identifying the state of the segment. See
        ``lib5c.parsers.bed.load_features()``.
    segmentation_colors :'auto' or func(str -> valid matplotlib color or dict)
        Pass 'auto' to assign random colors to each segment state in the
        segmentation. Alternatively, pass a function which takes in a state id
        as a string and returns a valid matplotlib color. Finally, you may also
        pass a dict whose keys are the state ids as strings and whose values are
        matplotlib colors.
    communities : List[Tuple[int, int]]
        List of communites to outline on the heatmap. Communities should be
        represented as (start, end) tuples.
    chipseq_track_line_width : float
        Line width to use when plotting ChIP-seq track signal, if any tracks are
        plotted.
    """
    # the array might be normalized or clipped during the plotting process
    # make a copy to prevent modifying the original
    array_copy = np.copy(array)

    # make pixelmap if necessary
    if not (pixelmap or regional_pixelmap):
        pixelmap = load_primermap(primer_file)
        warnings.warn(
            'the primer_file kwarg in lib5c.plotters.plot_heatmap() is '
            'deprecated\n'
            'it is recommended to pass the pixelmap kwarg instead',
            DeprecationWarning)
    if pixelmap and region:
        regional_pixelmap = pixelmap[region]

    # gene track element sizes
    gene_track_nominal_width = 80
    gene_track_params = {
        'ruler_tick_height'  :
            1.0 * float(len(array_copy)) / gene_track_nominal_width,
        'ruler_text_baseline':
            3.5 * float(len(array_copy)) / gene_track_nominal_width,
        'ruler_height'       : 4.0 * float(
            len(array_copy)) / gene_track_nominal_width,
        'row_height'         : 2.0 * float(
            len(array_copy)) / gene_track_nominal_width,
        'padding'            : 0.2 * float(
            len(array_copy)) / gene_track_nominal_width,
        'bar_height'         : 0.6 * float(
            len(array_copy)) / gene_track_nominal_width,
        'hpadding'           : 0.6 * float(
            len(array_copy)) / gene_track_nominal_width
    }

    # establish kwargs for rectangles used in gene and ChIP-seq tracks
    chipseq_rect_kwargs = {'color': 'k', 'lw': chipseq_track_line_width}
    rect_kwargs = {'color': 'k'}

    # turn zoom_window duple into an object
    if zoom_window and type(zoom_window) != dict:
        zoom_window = make_zoom_window(zoom_window[0], zoom_window[1],
                                       regional_pixelmap)

    # find the bin ranges on each axis if this heatmap should be zoomed
    min_x_bin = None
    max_x_bin = None
    min_y_bin = None
    max_y_bin = None
    if zoom_window:
        min_x_bin = zoom_window['x_start']
        max_x_bin = zoom_window['x_start'] + zoom_window['size'] - 1
        min_y_bin = zoom_window['y_start']
        max_y_bin = zoom_window['y_start'] + zoom_window['size'] - 1

    # handle bigwig input
    processed_tracks = []
    nonce = str(uuid.uuid4())[:7]
    for track in tracks:
        if track.endswith('.bw'):
            temp_filename = os.path.splitext(track)[0] + '_' + nonce + '.bdg'
            chrom = regional_pixelmap[0]['chrom']
            if zoom_window:
                start = regional_pixelmap[min(min_x_bin, min_y_bin)]['start']
                end = regional_pixelmap[max(max_x_bin, max_y_bin)]['end']
            else:
                start = regional_pixelmap[0]['start']
                end = regional_pixelmap[-1]['end']
            cmd = 'bigWigToBedGraph -chrom=%s -start=%i -end=%i %s %s' % \
                  (chrom, start, end, track, temp_filename)
            print cmd
            exit_code = subprocess.call(cmd, shell=True)
            if exit_code:
                warnings.warn(
                    'call to bigWigToBedGraph failed\n'
                    'perhaps it is not installed or not on the PATH?\n',
                    RuntimeWarning
                )
            else:
                processed_tracks.append(temp_filename)
        else:
            processed_tracks.append(track)
    tracks = processed_tracks

    # prepare gene tracks
    hrows = None
    vrows = None
    rows = None
    hsegments = None
    vsegments = None
    segments = None
    gene_track_height = 0
    if gene_track is not None:
        gene_file = get_gene_track_file(gene_track, regional_pixelmap)
        if zoom_window:
            hrows = pack_genes(
                get_intersecting_genes(gene_file, regional_pixelmap,
                                       len(array_copy), min_bin=min_x_bin,
                                       max_bin=max_x_bin), gene_track_params[
                    'hpadding'])
            vrows = pack_genes(
                get_intersecting_genes(gene_file, regional_pixelmap,
                                       len(array_copy), min_bin=min_y_bin,
                                       max_bin=max_y_bin),
                gene_track_params['hpadding'])
            gene_track_height = gene_track_params['ruler_height'] + max(len(
                hrows), len(vrows)) \
                * gene_track_params['row_height']
            if segmentation:
                hsegments = get_intersecting_segments(segmentation,
                                                      regional_pixelmap,
                                                      len(array_copy),
                                                      min_bin=min_x_bin,
                                                      max_bin=max_x_bin)
                vsegments = get_intersecting_segments(segmentation,
                                                      regional_pixelmap,
                                                      len(array_copy),
                                                      min_bin=min_y_bin,
                                                      max_bin=max_y_bin)
        else:
            rows = pack_genes(
                get_intersecting_genes(gene_file, regional_pixelmap,
                                       len(array_copy)),
                gene_track_params['hpadding'])
            gene_track_height = gene_track_params['ruler_height'] + \
                len(rows) * gene_track_params['row_height']
            if segmentation:
                segments = get_intersecting_segments(segmentation,
                                                     regional_pixelmap,
                                                     len(array_copy))

    # create default segmentation_colors
    segmentation_colors_function = None
    if segmentation:
        if segmentation_colors == 'auto':
            # get the list of unique id's
            segment_ids = set()
            for chrom in segmentation.keys():
                for segment in segmentation[chrom]:
                    segment_ids.add(segment['id'])
            segment_ids = list(segment_ids)

            # a number that determines the spacing between the color indices
            # (out of 256) with which to plot the different clusters
            color_multiplier = 256 / max(len(segment_ids) - 1, 1)
            colors = [cm.gist_ncar(i * color_multiplier)
                      for i in range(len(segment_ids))]
            segmentation_colors_dict = {segment_ids[i]: colors[i]
                                        for i in range(len(segment_ids))}
            segmentation_colors_function = segmentation_colors_dict.__getitem__
        elif type(segmentation_colors) == dict:
            segmentation_colors_function = segmentation_colors.__getitem__
        else:
            segmentation_colors_function = segmentation_colors

    # clear the figure
    plt.clf()

    # normalize heatmap
    if normalize:
        array_copy -= np.amin(array_copy)
        if not np.amax(array_copy) == 0:
            array_copy /= np.amax(array_copy)

    # calculate colorscale
    if not colorscale:
        flattened_array = flatten_regional_counts(array_copy, discard_nan=True)
        colorscale = [np.min(flattened_array), np.max(flattened_array)]

    # calculate track height
    track_height = relative_height * len(array_copy)

    # gridspec
    magic_numbers = [0.3, 0.24]
    grid_height = len(tracks) + 2
    grid_width = len(tracks) + 2
    if show_colorscale:
        grid_width += 1
    height_ratios = np.repeat([track_height], grid_height)
    height_ratios[0] = len(array_copy)
    width_ratios = np.repeat([track_height], grid_width)
    width_ratios[len(tracks)] = gene_track_height
    height_ratios[1] = gene_track_height
    if show_colorscale:
        width_ratios[-2] = len(array_copy)
    else:
        width_ratios[-1] = len(array_copy)
    gs = GridSpec(grid_height, grid_width, height_ratios=height_ratios,
                  width_ratios=width_ratios, wspace=0.00, hspace=0.00,
                  left=magic_numbers[int(show_colorscale)])
    heatmap = plt.subplot(gs[0, len(tracks) + 1])
    trackgh = plt.subplot(gs[1, len(tracks) + 1])
    trackgv = plt.subplot(gs[0, len(tracks)])
    track1v = None
    track2v = None
    track3v = None
    track4v = None
    track4h = None
    track3h = None
    track2h = None
    track1h = None
    vtracks = [trackgv]
    htracks = [trackgh]
    if len(tracks) == 1:
        track1v = plt.subplot(gs[0, 0])
        track1h = plt.subplot(gs[2, 2])
        vtracks.extend([track1v])
        htracks.extend([track1h])
    if len(tracks) == 2:
        track1v = plt.subplot(gs[0, 0])
        track2v = plt.subplot(gs[0, 1])
        track2h = plt.subplot(gs[2, 3])
        track1h = plt.subplot(gs[3, 3])
        vtracks.extend([track1v, track2v])
        htracks.extend([track1h, track2h])
    if len(tracks) == 3:
        track1v = plt.subplot(gs[0, 0])
        track2v = plt.subplot(gs[0, 1])
        track3v = plt.subplot(gs[0, 2])
        track3h = plt.subplot(gs[2, 4])
        track2h = plt.subplot(gs[3, 4])
        track1h = plt.subplot(gs[4, 4])
        vtracks.extend([track1v, track2v, track3v])
        htracks.extend([track1h, track2h, track3h])
    if len(tracks) == 4:
        track1v = plt.subplot(gs[0, 0])
        track2v = plt.subplot(gs[0, 1])
        track3v = plt.subplot(gs[0, 2])
        track4v = plt.subplot(gs[0, 3])
        track4h = plt.subplot(gs[2, 5])
        track3h = plt.subplot(gs[3, 5])
        track2h = plt.subplot(gs[4, 5])
        track1h = plt.subplot(gs[5, 5])
        vtracks.extend([track1v, track2v, track3v, track4v])
        htracks.extend([track1h, track2h, track3h, track4h])
    colorsc = None
    if show_colorscale:
        colorsc = plt.subplot(gs[0, grid_width - 1])

    # set aspects
    heatmap.set_aspect('equal', adjustable='box', anchor='SW')
    for track in vtracks:
        track.set_aspect('equal', adjustable='box', anchor='SE')
    for track in htracks:
        track.set_aspect('equal', adjustable='box', anchor='NW')
    if show_colorscale:
        colorsc.set_aspect('auto', adjustable='box', anchor='SW')

    # set limits
    if zoom_window:
        heatmap.set_xlim([0, zoom_window['size']])
        heatmap.set_ylim([zoom_window['size'], 0])
    else:
        heatmap.set_xlim([0, len(array_copy)])
        heatmap.set_ylim([len(array_copy), 0])
    for track in vtracks:
        track.set_xlim([0, track_height])
        track.set_ylim([len(array_copy), 0])
    for track in htracks:
        track.set_xlim([0, len(array_copy)])
        track.set_ylim([0, track_height])
    trackgv.set_xlim([0, gene_track_height])
    trackgh.set_ylim([0, gene_track_height])

    # calculate max track heights
    chipseq_coord_max_track_heights = []
    if track_scales == "auto-all":
        chipseq_coord_max_track_height = 0
        for track in tracks:
            temp = get_max_height(
                get_intersecting_peaks(track, regional_pixelmap,
                                       len(array_copy)))
            chipseq_coord_max_track_height = max(temp,
                                                 chipseq_coord_max_track_height)
        for track in tracks:
            chipseq_coord_max_track_heights.append(
                chipseq_coord_max_track_height)
    elif track_scales == "auto-each":
        for track in tracks:
            temp = get_max_height(
                get_intersecting_peaks(track, regional_pixelmap,
                                       len(array_copy)))
            chipseq_coord_max_track_heights.append(temp)
    elif track_scales == "auto-pairs":
        for i in range(0, len(tracks), 2):
            temp_even = get_max_height(
                get_intersecting_peaks(tracks[i], regional_pixelmap,
                                       len(array_copy)))
            temp_odd = 0
            if len(tracks) > i + 1:
                temp_odd = get_max_height(
                    get_intersecting_peaks(tracks[i + 1], regional_pixelmap,
                                           len(array_copy)))
            chipseq_coord_max_track_heights.append(max(temp_even, temp_odd))
            chipseq_coord_max_track_heights.append(max(temp_even, temp_odd))
    elif isinstance(track_scales, numbers.Number):
        chipseq_coord_max_track_heights = [track_scales] * len(tracks)
    elif isinstance(track_scales, list):
        if len(track_scales) == len(tracks):
            for track_scale in track_scales:
                chipseq_coord_max_track_heights.append(track_scale)
        elif len(track_scales) == (len(tracks) + 1) / 2:
            for track_scale in track_scales:
                chipseq_coord_max_track_heights.append(track_scale)
                chipseq_coord_max_track_heights.append(track_scale)
    else:
        for track in tracks:
            temp = get_max_height(
                get_intersecting_peaks(track, regional_pixelmap,
                                       len(array_copy)))
            chipseq_coord_max_track_heights.append(temp)

    # resolve cmap
    if type(cmap) == str:
        cmap = get_colormap(cmap)

    # honor track_scales_scalar
    chipseq_coord_max_track_heights = [
        track_scales_scalar * th for th in chipseq_coord_max_track_heights]

    # plot on the axes
    if zoom_window:
        im = heatmap.imshow(array_copy[min_y_bin:max_y_bin + 1,
                            min_x_bin:max_x_bin + 1], interpolation='none',
                            vmin=colorscale[0],
                            vmax=colorscale[1], cmap=cmap,
                            extent=[0, zoom_window['size'], zoom_window['size'],
                                    0])
    else:
        im = heatmap.imshow(array_copy, interpolation='none',
                            vmin=colorscale[0],
                            vmax=colorscale[1], cmap=cmap,
                            extent=[0, len(array_copy), len(array_copy), 0])
    if len(tracks) > 0:
        if zoom_window:
            plot_htrack(get_intersecting_peaks(tracks[0], regional_pixelmap,
                                               len(array_copy), min_x_bin,
                                               max_x_bin),
                        track1h, tracks[0], chipseq_coord_max_track_heights[
                            0], show_track_labels=show_track_labels,
                        rect_kwargs=chipseq_rect_kwargs)
            plot_vtrack(get_intersecting_peaks(tracks[0], regional_pixelmap,
                                               len(array_copy), min_y_bin,
                                               max_y_bin),
                        track1v, tracks[0], chipseq_coord_max_track_heights[0],
                        show_track_labels=show_track_labels,
                        rect_kwargs=chipseq_rect_kwargs)
        else:
            plot_track(get_intersecting_peaks(tracks[0], regional_pixelmap,
                                              len(array_copy)), track1h,
                       track1v, tracks[0],
                       chipseq_coord_max_track_heights[0],
                       show_track_labels=show_track_labels,
                       rect_kwargs=chipseq_rect_kwargs)
    if len(tracks) > 1:
        if zoom_window:
            plot_htrack(get_intersecting_peaks(tracks[1], regional_pixelmap,
                                               len(array_copy), min_x_bin,
                                               max_x_bin),
                        track2h, tracks[1], chipseq_coord_max_track_heights[
                            1], show_track_labels=show_track_labels,
                        rect_kwargs=chipseq_rect_kwargs)
            plot_vtrack(get_intersecting_peaks(tracks[1], regional_pixelmap,
                                               len(array_copy), min_y_bin,
                                               max_y_bin),
                        track2v, tracks[1], chipseq_coord_max_track_heights[1],
                        show_track_labels=show_track_labels,
                        rect_kwargs=chipseq_rect_kwargs)
        else:
            plot_track(get_intersecting_peaks(tracks[1], regional_pixelmap,
                                              len(array_copy)), track2h,
                       track2v, tracks[1],
                       chipseq_coord_max_track_heights[1],
                       show_track_labels=show_track_labels,
                       rect_kwargs=chipseq_rect_kwargs)
    if len(tracks) > 2:
        if zoom_window:
            plot_htrack(get_intersecting_peaks(tracks[2], regional_pixelmap,
                                               len(array_copy), min_x_bin,
                                               max_x_bin),
                        track3h, tracks[2], chipseq_coord_max_track_heights[2],
                        show_track_labels=show_track_labels,
                        rect_kwargs=chipseq_rect_kwargs)
            plot_vtrack(get_intersecting_peaks(tracks[2], regional_pixelmap,
                                               len(array_copy), min_y_bin,
                                               max_y_bin),
                        track3v, tracks[2], chipseq_coord_max_track_heights[2],
                        show_track_labels=show_track_labels,
                        rect_kwargs=chipseq_rect_kwargs)
        else:
            plot_track(get_intersecting_peaks(tracks[2], regional_pixelmap,
                                              len(array_copy)), track3h,
                       track3v,
                       tracks[2], chipseq_coord_max_track_heights[2],
                       show_track_labels=show_track_labels,
                       rect_kwargs=chipseq_rect_kwargs)
    if len(tracks) > 3:
        if zoom_window:
            plot_htrack(get_intersecting_peaks(tracks[3], regional_pixelmap,
                                               len(array_copy), min_x_bin,
                                               max_x_bin),
                        track4h, tracks[3], chipseq_coord_max_track_heights[3],
                        show_track_labels=show_track_labels,
                        rect_kwargs=chipseq_rect_kwargs)
            plot_vtrack(get_intersecting_peaks(tracks[3], regional_pixelmap,
                                               len(array_copy), min_y_bin,
                                               max_y_bin),
                        track4v, tracks[3], chipseq_coord_max_track_heights[3],
                        show_track_labels=show_track_labels,
                        rect_kwargs=chipseq_rect_kwargs)
        else:
            plot_track(get_intersecting_peaks(tracks[3], regional_pixelmap,
                                              len(array_copy)), track4h,
                       track4v, tracks[3],
                       chipseq_coord_max_track_heights[3],
                       show_track_labels=show_track_labels,
                       rect_kwargs=chipseq_rect_kwargs)
    if show_colorscale:
        plt.colorbar(im, cax=colorsc)

    # remove temporary bedgraph files
    for track in tracks:
        if nonce in track:
            os.remove(track)

    # outline clusters
    if clusters:
        if cluster_colors:
            # resolve line width
            base_linewidth = cluster_weight
            if type(cluster_weight) == str:
                if zoom_window:
                    base_linewidth = float(cluster_weight[:-1]) / \
                        zoom_window['size']
                else:
                    base_linewidth = float(cluster_weight[:-1]) / \
                        len(array_copy)

            # resolve outline line width
            outline_linewidth = base_linewidth + 2
            if outline_color and outline_weight:
                if type(outline_weight) == str:
                    outline_linewidth = float(
                        outline_weight[:-1]) * base_linewidth
                else:
                    outline_linewidth = base_linewidth + outline_weight

            # default zoom_window: the whole region
            outlining_zoom_window = zoom_window
            if not outlining_zoom_window:
                outlining_zoom_window = {'x_start': 0,
                                         'y_start': 0,
                                         'size'   : len(array_copy)}

            # resolve colors
            if outline_color:
                outline_clusters(heatmap, clusters, outlining_zoom_window,
                                 [outline_color] * len(clusters),
                                 outline_linewidth)
            if cluster_colors == 'random':
                cluster_colors = None
            elif type(cluster_colors) != list:
                cluster_colors = [cluster_colors] * len(clusters)

            # outline clusters
            outline_clusters(heatmap, clusters, outlining_zoom_window,
                             cluster_colors, base_linewidth)
        if cluster_labels:
            # handle special values
            if cluster_labels == "indices":
                cluster_labels = range(len(clusters))
            # check cluster length
            if len(cluster_labels) == len(clusters):
                for i in range(len(clusters)):
                    centroid = calculate_centroid(clusters[i]) + np.array([
                        0.5, 0.5])
                    if zoom_window:
                        centroid[0] -= zoom_window['x_start']
                        centroid[1] -= zoom_window['y_start']
                    if centroid[0] > 0 and centroid[1] > 0:
                        heatmap.text(centroid[0], centroid[1],
                                     str(cluster_labels[i]), fontsize=7,
                                     ha='center', va='center')
            else:
                warnings.warn('len(cluster_labels) != len(clusters)',
                              RuntimeWarning)

    # handle communities
    if communities:
        boundary = None
        boundary = {'chrom': pixelmap[region][0]['chrom'],
                    'start': pixelmap[region][0]['start'],
                    'end'  : pixelmap[region][-1]['end']}
        colors = []

        for i in range(len(communities)):
            start = float(communities[i][0] - boundary['start']) * \
                len(array_copy) / (boundary['end'] - boundary['start'])
            end = float(communities[i][1] - boundary['start']) * \
                len(array_copy) / (boundary['end'] - boundary['start'])

            heatmap.plot([end, end], [start, end], color='g', linestyle='-',
                         linewidth=2)
            heatmap.plot([start, end], [start, start], color='g', linestyle='-',
                         linewidth=2)

    # clean ticks
    heatmap.get_xaxis().set_ticks([])
    heatmap.get_yaxis().set_ticks([])
    for track in vtracks:
        track.get_xaxis().set_ticks([])
        track.get_yaxis().set_ticks([])
    for track in htracks:
        track.get_xaxis().set_ticks([])
        track.get_yaxis().set_ticks([])

    # tweak ticks on colorscale
    if show_colorscale:
        colorax = colorsc.twinx()
        colorsc.get_xaxis().set_ticks([])
        colorsc.get_yaxis().set_ticks([])
        colorax.get_yaxis().set_ticks([0, len(array_copy)])
        colorax.get_yaxis().set_ticklabels(colorscale)

    # plot gene track
    if gene_track:
        if zoom_window:
            plot_hgene(hrows, trackgh, regional_pixelmap[min_x_bin]['start'],
                       regional_pixelmap[max_x_bin]['end'],
                       regional_pixelmap[min_x_bin]['chrom'], gene_track_params,
                       segments=hsegments,
                       segmentation_colors=segmentation_colors_function,
                       rect_kwargs=rect_kwargs)
            plot_vgene(vrows, trackgv, regional_pixelmap[min_y_bin]['start'],
                       regional_pixelmap[max_y_bin]['end'],
                       regional_pixelmap[min_y_bin]['chrom'], gene_track_params,
                       segments=vsegments,
                       segmentation_colors=segmentation_colors_function,
                       rect_kwargs=rect_kwargs)
        else:
            plot_hgene(rows, trackgh, regional_pixelmap[0]['start'],
                       regional_pixelmap[-1]['end'],
                       regional_pixelmap[0]['chrom'], gene_track_params,
                       segments=segments,
                       segmentation_colors=segmentation_colors_function,
                       rect_kwargs=rect_kwargs)
            plot_vgene(rows, trackgv, regional_pixelmap[0]['start'],
                       regional_pixelmap[-1]['end'],
                       regional_pixelmap[0]['chrom'], gene_track_params,
                       segments=segments,
                       segmentation_colors=segmentation_colors_function,
                       rect_kwargs=rect_kwargs)

    # save
    plt.savefig(outfile, bbox_inches='tight', dpi=800)


def calculate_centroid(cluster):
    """
    Calculates the centroid of a cluster.

    Parameters
    ---------
    cluster : list of dicts
        Each dict represents a pixel in the cluster. These dicts have the
        following structure::

            {
                'x' : int,
                'y' : int
            }

        Here x and y represent the x and y coordinates of the pixel within the
        region.

    Returns
    -------
    1 x 2 numpy array
        The centroid of the cluster.
    """
    vector_sum = np.array([0, 0])
    for peak in cluster:
        vector_sum += np.array([peak['x'], peak['y']])
    return vector_sum / float(len(cluster))


def make_zoom_window(x_range, y_range, regional_pixelmap):
    """
    Creates a zoom window object windowing the given genomic ranges.

    Parameters
    ----------
    x_range, y_range : string
        String represenations of genomic ranges that should be included in
        the zoom window. For example,
        'chr3:34459302-34576915'.
    region : string
        The string name of the region being plotted.
    pixelmap : dict of lists of dicts
        The keys of the outer dict are region names. The values are lists,
        where the ith entry represents the ith bin in
        that region. Bins are represented as dicts with at least the following
        structure::

            {
                'chrom': string,
                'start': int,
                'end'  : int
            }

        See lib5c.parsers.primers.get_pixelmap().

    Returns
    -------
    dict
        A dict with the following structure::

            {
                'x_start': int,
                'y_start': int,
                'size': int
            }

        where x_start and y_start represent the indices of the lowest-indexed
        bin to include along the x-axis and the y-axis, respectively, and size
        represents both the width and the height of the square zoom window in
        bins.
    """
    min_x_bin, max_x_bin = find_extreme_bins(regional_pixelmap,
                                             parse_genomic_range(x_range))
    min_y_bin, max_y_bin = find_extreme_bins(regional_pixelmap,
                                             parse_genomic_range(y_range))
    x_size = max_x_bin - min_x_bin + 1
    y_size = max_y_bin - min_y_bin + 1
    size = max(x_size, y_size)
    # shift the anchor if necessary
    x_shift = (len(regional_pixelmap) - 1) - (min_x_bin + size - 1)
    y_shift = (len(regional_pixelmap) - 1) - (min_y_bin + size - 1)
    if x_shift < 0:
        min_x_bin += x_shift
    if y_shift < 0:
        min_y_bin += y_shift
    return {'x_start': min_x_bin, 'y_start': min_y_bin, 'size': size}


def find_extreme_bins(regional_pixelmap, range_dict):
    min_bin = 0
    while regional_pixelmap[min_bin]['start'] <= range_dict['start']:
        min_bin += 1
    max_bin = len(regional_pixelmap) - 1
    while regional_pixelmap[max_bin]['end'] > range_dict['end']:
        max_bin -= 1
    return max(0, min_bin - 1), min(max_bin + 1, len(regional_pixelmap) - 1)


def parse_genomic_range(genomic_range):
    chrom, rest = genomic_range.strip().split(':')
    pieces = rest.strip().split('-')
    start = int(pieces[0].strip())
    end = int(pieces[1].strip())
    return {'chrom': chrom, 'start': start, 'end': end}


def get_intersecting_peaks(peak_file, regional_pixelmap, plot_size,
                           min_bin=None, max_bin=None):
    # load in the information we need
    boundary = None
    if min_bin is None or max_bin is None:
        min_bin = 0
        max_bin = -1
    boundary = {'chrom': regional_pixelmap[min_bin]['chrom'],
                'start': regional_pixelmap[min_bin]['start'],
                'end'  : regional_pixelmap[max_bin]['end']}

    peaks = load_features(peak_file)[boundary['chrom']]

    # filter the peaks based on the boundary information
    filtered_peaks = filter(
        lambda x: (boundary['start'] <= x['start'] <=
                   boundary['end']) or
                  (boundary['start'] <= x['end'] <= boundary['end']) or
                  (x['end'] >= boundary['end'] and
                   x['start'] <= boundary['start']), peaks)

    # convert peak coordinates to bin coordinates
    for peak in filtered_peaks:
        start = float(peak['start'] - boundary['start']) * plot_size / \
            (boundary['end'] - boundary['start'])
        end = float(peak['end'] - boundary['start']) * plot_size / \
            (boundary['end'] - boundary['start'])
        peak['start'] = start
        peak['end'] = end

    return filtered_peaks


def get_intersecting_segments(segmentation, regional_pixelmap, plot_size,
                              min_bin=None, max_bin=None):
    # load in the information we need
    boundary = None
    if min_bin is None or max_bin is None:
        min_bin = 0
        max_bin = -1
    boundary = {'chrom': regional_pixelmap[min_bin]['chrom'],
                'start': regional_pixelmap[min_bin]['start'],
                'end'  : regional_pixelmap[max_bin]['end']}

    segments = segmentation[boundary['chrom']]

    # filter the peaks based on the boundary information
    filtered_segments = filter(
        lambda x: (boundary['start'] <= x['start'] <= boundary['end']) or
                  (boundary['start'] <= x['end'] <= boundary['end']) or
                  (x['end'] >= boundary['end'] and
                   x['start'] <= boundary['start']), segments)

    # we are about to do an in-place coordinate conversion, so we should not do
    # that on the segments which are still bound to a kwarg that the user passed
    # to us
    filtered_segments_copy = deepcopy(filtered_segments)

    # convert peak coordinates to bin coordinates
    for segment in filtered_segments_copy:
        start = float(segment['start'] - boundary['start']) * plot_size / \
            (boundary['end'] - boundary['start'])
        end = \
            float(segment['end'] - boundary['start']) * plot_size / \
            (boundary['end'] - boundary['start'])
        segment['start'] = start
        segment['end'] = end

    return filtered_segments_copy


def get_intersecting_genes(gene_file, regional_pixelmap, plot_size,
                           min_bin=None, max_bin=None):
    # load in the information we need
    boundary = None
    if min_bin is None or max_bin is None:
        min_bin = 0
        max_bin = -1
    boundary = {'chrom': regional_pixelmap[min_bin]['chrom'],
                'start': regional_pixelmap[min_bin]['start'],
                'end'  : regional_pixelmap[max_bin]['end']}

    all_genes = load_genes(gene_file)

    # make sure there are actually genes in this region
    if not boundary['chrom'] in all_genes:
        return []
    genes = all_genes[boundary['chrom']]

    # filter the genes based on the boundary information
    filtered_genes = filter(
        lambda x: (boundary['start'] <= x['start'] <= boundary['end']) or
                  (boundary['start'] <= x['end'] <= boundary['end']) or
                  (x['end'] >= boundary['end'] and
                   x['start'] <= boundary['start']), genes)

    # convert peak coordinates to bin coordinates
    for gene in filtered_genes:
        start = float(gene['start'] - boundary['start']) * plot_size / \
            (boundary['end'] - boundary['start'])
        end = \
            float(gene['end'] - boundary['start']) * plot_size / \
            (boundary['end'] - boundary['start'])
        gene['start'] = start
        gene['end'] = end

        for block in gene['blocks']:
            start = float(block['start'] - boundary['start']) * plot_size / \
                (boundary['end'] - boundary['start'])
            end = \
                float(block['end'] - boundary['start']) * plot_size / \
                (boundary['end'] - boundary['start'])
            block['start'] = start
            block['end'] = end

    return filtered_genes


def plot_hgene(rows, gene_htrack, start, end, chrom, gene_track_params,
               segments=None, segmentation_colors=None, rect_kwargs=None):
    if rect_kwargs is None:
        rect_kwargs = {}

    # height and width of the track
    track_height = gene_htrack.get_ylim()[1]
    track_width = gene_htrack.get_xlim()[1]

    # draw segments
    if segments:
        for segment in segments:
            gene_htrack.add_artist(mpl.patches.Rectangle(
                (segment['start'], 0), segment['end'] - segment['start'],
                track_height, color=segmentation_colors(segment['id'])))

    # draw ticks and ruler
    for i in range(1, 4):
        gene_htrack.add_artist(mpl.patches.Rectangle(
            (track_width * i / 4.0,
             track_height - gene_track_params['ruler_tick_height']), 0.1,
            gene_track_params['ruler_tick_height'], **rect_kwargs))
        gene_htrack.text(
            track_width * i / 4.0,
            track_height - gene_track_params['ruler_text_baseline'],
            str(int(start + (end - start) * i / 4.0)), fontsize=7, ha='center',
            va='bottom')
    gene_htrack.text(
        track_width / 80,
        track_height - gene_track_params['ruler_text_baseline'], chrom,
        fontsize=7, ha='left', va='bottom')
    gene_htrack.text(
        track_width - track_width / 80,
        track_height - gene_track_params['ruler_text_baseline'],
        '%ikb' % ((end - start) / 1000), fontsize=7, ha='right', va='bottom')

    # create patches for each gene
    for i in range(len(rows)):
        top_coordinate = track_height - \
            gene_track_params['ruler_height'] - \
            i * gene_track_params['row_height'] - \
            gene_track_params['padding'] - \
            gene_track_params['bar_height']
        for gene in rows[i]:
            gene_htrack.add_artist(
                mpl.patches.Rectangle(
                    (gene['start'],
                     top_coordinate + gene_track_params[
                         'bar_height'] / 2 - 0.05),
                    gene['end'] - gene['start'], 0.1, **rect_kwargs))
            for block in gene['blocks']:
                gene_htrack.add_artist(
                    mpl.patches.Rectangle(
                        (block['start'], top_coordinate),
                        block['end'] - block['start'],
                        gene_track_params['bar_height'], **rect_kwargs))

            if gene['strand'] == '+':
                gene_htrack.plot(
                    [gene['start'] - gene_track_params['bar_height'] / 2,
                     gene['start']],
                    [top_coordinate + gene_track_params['bar_height'],
                     top_coordinate + gene_track_params['bar_height'] / 2],
                    'k-')
                gene_htrack.plot(
                    [gene['start'] - gene_track_params['bar_height'] / 2,
                     gene['start']],
                    [top_coordinate,
                     top_coordinate + gene_track_params['bar_height'] / 2],
                    'k-')
            else:
                gene_htrack.plot(
                    [gene['end'] + gene_track_params['bar_height'] / 2,
                     gene['end']],
                    [top_coordinate + gene_track_params['bar_height'],
                     top_coordinate + gene_track_params['bar_height'] / 2],
                    'k-')
                gene_htrack.plot(
                    [gene['end'] + gene_track_params['bar_height'] / 2,
                     gene['end']],
                    [top_coordinate,
                     top_coordinate + gene_track_params['bar_height'] / 2],
                    'k-')

    # clean ticks
    gene_htrack.get_yaxis().set_ticks([])


def plot_vgene(rows, gene_vtrack, start, end, chrom, gene_track_params,
               segments=None, segmentation_colors=None, rect_kwargs=None):
    if rect_kwargs is None:
        rect_kwargs = {}

    # height and width of the track
    track_height = gene_vtrack.get_xlim()[1]
    track_width = gene_vtrack.get_ylim()[0]

    # draw segments
    if segments:
        for segment in segments:
            gene_vtrack.add_artist(mpl.patches.Rectangle(
                (0, segment['start']), track_height,
                segment['end'] - segment['start'],
                color=segmentation_colors(segment['id'])))

    # draw ticks and ruler
    for i in range(1, 4):
        gene_vtrack.add_artist(mpl.patches.Rectangle(
            (track_height - gene_track_params['ruler_tick_height'],
             track_width * i / 4.0), gene_track_params['ruler_tick_height'],
            0.1, **rect_kwargs))
        gene_vtrack.text(
            track_height - gene_track_params['ruler_text_baseline'],
            track_width * i / 4.0, str(int(start + (end - start) * i / 4.0)),
            fontsize=7, ha='left', va='center', rotation=270)
    gene_vtrack.text(
        track_height - gene_track_params['ruler_text_baseline'],
        track_width / 80, chrom, fontsize=7, ha='left', va='top', rotation=270)
    gene_vtrack.text(
        track_height - gene_track_params['ruler_text_baseline'],
        track_width - track_width / 80, '%ikb' % ((end - start) / 1000),
        fontsize=7, ha='left', va='bottom', rotation=270)

    # create patches for each gene
    for i in range(len(rows)):
        left_coordinate = track_height - \
            gene_track_params['ruler_height'] - \
            i * gene_track_params['row_height'] - \
            gene_track_params['padding'] - \
            gene_track_params['bar_height']
        for gene in rows[i]:
            gene_vtrack.add_artist(mpl.patches.Rectangle(
                (left_coordinate + gene_track_params['bar_height'] / 2 - 0.05,
                 gene['start']), 0.1, gene['end'] - gene['start'],
                **rect_kwargs))
            for block in gene['blocks']:
                gene_vtrack.add_artist(mpl.patches.Rectangle(
                    (left_coordinate, block['start']),
                    gene_track_params['bar_height'],
                    block['end'] - block['start'], **rect_kwargs))

            if gene['strand'] == '+':
                gene_vtrack.plot(
                    [left_coordinate + gene_track_params['bar_height'],
                     left_coordinate + gene_track_params['bar_height'] / 2],
                    [gene['start'] - gene_track_params['bar_height'] / 2,
                     gene['start']],
                    'k-')
                gene_vtrack.plot(
                    [left_coordinate,
                     left_coordinate + gene_track_params['bar_height'] / 2],
                    [gene['start'] - gene_track_params['bar_height'] / 2,
                     gene['start']],
                    'k-')
            else:
                gene_vtrack.plot(
                    [left_coordinate + gene_track_params['bar_height'],
                     left_coordinate + gene_track_params['bar_height'] / 2],
                    [gene['end'] + gene_track_params['bar_height'] / 2,
                     gene['end']],
                    'k-')
                gene_vtrack.plot(
                    [left_coordinate,
                     left_coordinate + gene_track_params['bar_height'] / 2],
                    [gene['end'] + gene_track_params['bar_height'] / 2,
                     gene['end']],
                    'k-')

    # clean ticks
    gene_vtrack.get_xaxis().set_ticks([])


def pack_genes(genes, hpadding=0.0):
    # our data structures
    row_cursors = []
    rows = []

    # initialize the first row
    rows.append([])
    row_cursors.append(-10000)  # basically should be -Inf

    # main loop
    for gene in genes:
        gene_placed = False
        for i in range(len(rows)):
            if gene['start'] > row_cursors[i] + hpadding:
                row_cursors[i] = gene['end']
                rows[i].append(gene)
                gene_placed = True
                break
        if not gene_placed:
            rows.append([gene])
            row_cursors.append(gene['end'])

    return rows


def get_max_height(peaks):
    return reduce(lambda x, y: {'value': max(x['value'], y['value'])},
                  peaks)['value']


def plot_htrack(peaks, htrack, peak_file, max_height=None,
                show_track_labels=True, rect_kwargs=None):
    if rect_kwargs is None:
        rect_kwargs = {}

    # height of the track
    track_height = htrack.get_ylim()[1]

    if peaks:
        # normalize the height of the track
        if not max_height:
            max_height = get_max_height(peaks)
        scale_factor = max_height / track_height

        # create patches for each peak
        for peak in peaks:
            if 'value' not in peak:
                peak['value'] = 1
            htrack.add_artist(mpl.patches.Rectangle(
                (peak['start'], 0), peak['end'] - peak['start'],
                peak['value'] / scale_factor, **rect_kwargs))

    # clean ticks
    htrack.get_yaxis().set_ticks([])

    # add name
    if show_track_labels:
        dir, filename = os.path.split(peak_file)
        track_name, ext = os.path.splitext(filename)
        htrack.text(track_height / 10, track_height * 9 / 10, track_name,
                    fontsize=7, ha='left', va='top')

    # add max_peak_height
    if peaks:
        htrack.text(
            htrack.get_xlim()[1] - track_height / 10, track_height * 9 / 10,
            str(max_height), fontsize=7, ha='right', va='top')
    else:
        htrack.text(
            htrack.get_xlim()[1] - track_height / 10, track_height * 9 / 10,
            'no peaks in range', fontsize=7, ha='right', va='top')


def plot_vtrack(peaks, vtrack, peak_file, max_height=None,
                show_track_labels=True, rect_kwargs=None):
    if rect_kwargs is None:
        rect_kwargs = {}

    # height of the track
    track_height = vtrack.get_xlim()[1]
    track_width = vtrack.get_ylim()[0]

    if peaks:
        # normalize the height of the track
        if not max_height:
            max_height = get_max_height(peaks)
        scale_factor = max_height / track_height

        # create patches for each peak
        for peak in peaks:
            if 'value' not in peak:
                peak['value'] = 1
            vtrack.add_artist(mpl.patches.Rectangle(
                (0, peak['start']), peak['value'] / scale_factor,
                peak['end'] - peak['start'], **rect_kwargs))

    # clean ticks
    vtrack.get_xaxis().set_ticks([])

    # add name
    if show_track_labels:
        directory, filename = os.path.split(peak_file)
        track_name, ext = os.path.splitext(filename)
        vtrack.text(track_height * 9 / 10, track_width / 80, track_name,
                    fontsize=7, ha='right', va='top', rotation=270)

    # add max_peak_height
    if peaks:
        vtrack.text(
            track_height * 9 / 10, vtrack.get_ylim()[0] - track_height / 10,
            str(max_height), fontsize=7, ha='right', va='bottom', rotation=270)
    else:
        vtrack.text(
            track_height * 9 / 10, vtrack.get_ylim()[0] - track_height / 10,
            'no peaks in range', fontsize=7, ha='right', va='bottom',
            rotation=270)


def plot_track(peaks, htrack, vtrack, peak_file, max_height=None,
               show_track_labels=True, rect_kwargs=None):
    if rect_kwargs is None:
        rect_kwargs = {}

    # height of the track
    track_height = htrack.get_ylim()[1]
    track_width = vtrack.get_ylim()[0]

    if peaks:
        # normalize the height of the track
        if not max_height:
            max_height = get_max_height(peaks)
        scale_factor = max_height / track_height

        # create patches for each peak
        for peak in peaks:
            if 'value' not in peak:
                peak['value'] = 1
            htrack.add_artist(mpl.patches.Rectangle(
                (peak['start'], 0), peak['end'] - peak['start'],
                peak['value'] / scale_factor,
                **rect_kwargs))
            vtrack.add_artist(mpl.patches.Rectangle(
                (0, peak['start']), peak['value'] / scale_factor,
                peak['end'] - peak['start'], **rect_kwargs))

    # clean ticks
    htrack.get_yaxis().set_ticks([])
    vtrack.get_xaxis().set_ticks([])

    # add name
    if show_track_labels:
        directory, filename = os.path.split(peak_file)
        track_name, ext = os.path.splitext(filename)
        htrack.text(track_height / 10, track_height * 9 / 10, track_name,
                    fontsize=7, ha='left', va='top')
        vtrack.text(track_height * 9 / 10, track_width / 80, track_name,
                    fontsize=7, ha='right', va='top', rotation=270)

    # add max_peak_height
    if peaks:
        htrack.text(
            htrack.get_xlim()[1] - track_height / 10, track_height * 9 / 10,
            str(max_height), fontsize=7, ha='right', va='top')
        vtrack.text(
            track_height * 9 / 10, htrack.get_xlim()[1] - track_height / 10,
            str(max_height), fontsize=7, ha='right', va='bottom', rotation=270)
    else:
        htrack.text(
            htrack.get_xlim()[1] - track_height / 10, track_height * 9 / 10,
            'no peaks in range', fontsize=7, ha='right', va='top')
        vtrack.text(
            track_height * 9 / 10, htrack.get_xlim()[1] - track_height / 10,
            'no peaks in range', fontsize=7, ha='right', va='bottom',
            rotation=270)


def mirror_clusters(clusters):
    mirrored_clusters = []
    for cluster in clusters:
        mirrored_cluster = []
        for peak in cluster:
            mirrored_cluster.append(peak)
            query_peak = {'x': peak['y'],
                          'y': peak['x']}
            if query_peak not in cluster:
                mirrored_cluster.append(query_peak)
        mirrored_clusters.append(mirrored_cluster)
    return mirrored_clusters


def belongs_to(peak, cluster):
    for member in cluster:
        if peak['x'] == member['x'] and peak['y'] == member['y']:
            return True
    return False


def outline_clusters(ax, clusters, zoom_window, colors=None, line_width=1):
    # set default colors if not provided
    if not colors:
        # a number that determines the spacing between the color indices (out
        # of 256) with which to plot the different clusters
        color_multiplier = 256 / max(len(clusters) - 1, 1)
        colors = [cm.gist_ncar(i * color_multiplier)
                  for i in range(len(clusters))]

    # mirror the clusters
    clusters = mirror_clusters(clusters)

    # the logic here is that for each peak, we look at each neighbor, and if
    # the neighbor isn't in this cluster, we draw a line separating cluster
    # from not-cluster
    for i in range(len(clusters)):
        for peak in clusters[i]:
            # top
            query_peak = {'x': peak['x'], 'y': peak['y'] - 1}
            if not belongs_to(query_peak, clusters[i]):
                x = peak['x']
                y = peak['y']
                if zoom_window:
                    x -= zoom_window['x_start']
                    y -= zoom_window['y_start']
                ax.plot([x, x + 1], [y, y], c=colors[i], lw=line_width)

            # bottom
            query_peak = {'x': peak['x'], 'y': peak['y'] + 1}
            if not belongs_to(query_peak, clusters[i]):
                x = peak['x']
                y = peak['y']
                if zoom_window:
                    x -= zoom_window['x_start']
                    y -= zoom_window['y_start']
                ax.plot([x, x + 1], [y + 1, y + 1], c=colors[i], lw=line_width)

            # left
            query_peak = {'x': peak['x'] - 1, 'y': peak['y']}
            if not belongs_to(query_peak, clusters[i]):
                x = peak['x']
                y = peak['y']
                if zoom_window:
                    x -= zoom_window['x_start']
                    y -= zoom_window['y_start']
                ax.plot([x, x], [y, y + 1], c=colors[i], lw=line_width)

            # right
            query_peak = {'x': peak['x'] + 1, 'y': peak['y']}
            if not belongs_to(query_peak, clusters[i]):
                x = peak['x']
                y = peak['y']
                if zoom_window:
                    x -= zoom_window['x_start']
                    y -= zoom_window['y_start']
                ax.plot([x + 1, x + 1], [y, y + 1], c=colors[i], lw=line_width)


def get_gene_track_file(gene_track, regional_pixelmap):
    if gene_track in ['mm9']:
        directory, filename = os.path.split(__file__)
        if not directory:
            directory = '.'
        return '%d/gene_tracks/%g/%g_refseq_genes_%c.bed' \
            .replace('%d', directory) \
            .replace('%g', gene_track) \
            .replace('%c', regional_pixelmap[0]['chrom'])
    return gene_track.replace('%c', regional_pixelmap[0]['chrom'])


# test client
def main():
    from lib5c.plotters.colorscales import obs_over_exp_colorscale
    from lib5c.parsers.counts import load_counts
    from lib5c.parsers.bed import load_features
    from lib5c.parsers.primers import load_primermap

    counts = load_counts('test/test.counts')

    segmenatation = load_features('test/ES_segments.bed')
    segmentation_colors_dict = {'E1': 'green',
                                'E2': 'chartreuse',
                                'E3': 'red',
                                'E4': 'orange',
                                'E5': 'yellow',
                                'E6': 'white',
                                'E7': 'purple'}
    segmentation_colors = segmentation_colors_dict.__getitem__

    plot_heatmap(counts['Klf4'],
                 'test/heatmap_zoom_segmented',
                 tracks=['test/reduced_bedgraph.bed'],
                 pixelmap=load_primermap('test/bins.bed'),
                 region='Klf4',
                 show_colorscale=False,
                 cmap=obs_over_exp_colorscale,
                 zoom_window=('chr3:55040000-55180000',
                              'chr3:54900000-55040000'),
                 clusters=[[{'x': 18, 'y': 3},
                            {'x': 19, 'y': 3},
                            {'x': 18, 'y': 4},
                            {'x': 19, 'y': 4},
                            {'x': 18, 'y': 5},
                            {'x': 19, 'y': 5}],
                           [{'x': 15, 'y': 3},
                            {'x': 15, 'y': 4},
                            {'x': 15, 'y': 5}]],
                 outline_color='lime',
                 cluster_colors='random',
                 cluster_weight='200x',
                 cluster_labels=['hi', 'bye'],
                 segmentation=segmenatation,
                 segmentation_colors=segmentation_colors)
    plot_heatmap(counts['Klf4'],
                 'test/heatmap',
                 tracks=np.repeat(['test/reduced_bedgraph.bed'], 4),
                 track_scales_scalar=2.0,
                 pixelmap=load_primermap('test/bins.bed'),
                 region='Klf4',
                 show_colorscale=True,
                 cmap=obs_over_exp_colorscale,
                 clusters=[[{'x': 18, 'y': 3},
                            {'x': 19, 'y': 3},
                            {'x': 18, 'y': 4},
                            {'x': 19, 'y': 4},
                            {'x': 18, 'y': 5},
                            {'x': 19, 'y': 5}],
                           [{'x': 15, 'y': 3},
                            {'x': 15, 'y': 4},
                            {'x': 15, 'y': 5}]],
                 cluster_colors=['red', 'blue'],
                 segmentation=segmenatation)
    plot_heatmap(counts['Klf4'],
                 'test/heatmap_zoom',
                 tracks=[],
                 pixelmap=load_primermap('test/bins.bed'),
                 region='Klf4',
                 show_colorscale=False,
                 cmap=obs_over_exp_colorscale,
                 zoom_window=('chr3:55040000-55180000',
                              'chr3:54900000-55040000'),
                 clusters=[[{'x': 18, 'y': 3},
                            {'x': 19, 'y': 3},
                            {'x': 18, 'y': 4},
                            {'x': 19, 'y': 4},
                            {'x': 18, 'y': 5},
                            {'x': 19, 'y': 5}],
                           [{'x': 15, 'y': 3},
                            {'x': 15, 'y': 4},
                            {'x': 15, 'y': 5}]],
                 outline_color='lime',
                 cluster_colors='random',
                 cluster_weight='200x',
                 cluster_labels=['hi', 'bye'])
    plot_heatmap(counts['Klf4'],
                 'test/heatmap_zoom_segmented2',
                 tracks=['test/reduced_bedgraph.bed'],
                 pixelmap=load_primermap('test/bins.bed'),
                 region='Klf4',
                 show_colorscale=False,
                 cmap=obs_over_exp_colorscale,
                 zoom_window=('chr3:55040000-55180000',
                              'chr3:54900000-55040000'),
                 clusters=[[{'x': 18, 'y': 3},
                            {'x': 19, 'y': 3},
                            {'x': 18, 'y': 4},
                            {'x': 19, 'y': 4},
                            {'x': 18, 'y': 5},
                            {'x': 19, 'y': 5}],
                           [{'x': 15, 'y': 3},
                            {'x': 15, 'y': 4},
                            {'x': 15, 'y': 5}]],
                 outline_color='lime',
                 cluster_colors='random',
                 cluster_weight='200x',
                 outline_weight='1.5x',
                 cluster_labels=['hi', 'bye'],
                 segmentation=segmenatation,
                 segmentation_colors=segmentation_colors_dict)
    plot_heatmap(counts['Klf4'],
                 'test/heatmap_newgenes',
                 regional_pixelmap=load_primermap('test/bins.bed')['Klf4'],
                 cmap='obs_over_exp')
    plot_heatmap(counts['Klf4'],
                 'test/heatmap_CTCF_zoomed',
                 zoom_window=('chr3:55040000-55180000',
                              'chr3:54900000-55040000'),
                 gene_track='test/CTCF_consensus.bed',
                 regional_pixelmap=load_primermap('test/bins.bed')['Klf4'],
                 cmap='obs_over_exp')


# test client for testing communities
def main_communities():
    from lib5c.parsers.counts import load_counts
    import glob
    import sys

    colorscale_input = {}
    colorscale = {}
    scale = mpl.colors.LinearSegmentedColormap.from_list('buworb',
                                                         colors=['#666666',
                                                                 '#C2C2C2',
                                                                 '#E0E0E0',
                                                                 'white',
                                                                 '#ffb833',
                                                                 'red',
                                                                 'darkred',
                                                                 'darkred',
                                                                 'black'])
    scale.set_under('#333333')
    colorscale_input['obs'] = 'input/observed_colorscales.txt'

    input = open(colorscale_input['obs'], 'r')
    for line in input:
        if line[0] == '#':
            continue
        if 'obs' not in colorscale:
            colorscale['obs'] = {}
        temp = line.strip().split('\t')
        colorscale['obs'][temp[0]] = [float(temp[1]), float(temp[2])]
    input.close()

    gamma_min = float(sys.argv[2])
    gamma_max = float(sys.argv[3])

    gammas = np.arange(gamma_min, gamma_max, 0.01)
    gammas = [str(i) for i in gammas]

    community = {}
    community_input = glob.glob(
        'output/results_files/consensus_communities/' + sys.argv[1])

    directory = 'output/heatmaps'
    if not os.path.exists(directory):
        os.makedirs(directory)

    replicates = glob.glob('output/*_obs.counts')

    for text in community_input:
        input = open(text, 'r')
        threshold = text.split('/')[3].split('_')[6]
        rep_name = text.split('/')[3].split('_')[3] + '_' + \
            text.split('/')[3].split('_')[4]
        # threshold = re.findall(r"[-+]?\d*\.\d+|\d+", text) # Extract
        # numbers from the file name
        for line in input:
            if line[0] == '#':
                continue
            temp = line.strip().split('\t')
            if temp[1] not in gammas:
                continue
            else:
                if rep_name not in community:
                    community[rep_name] = {}
                if temp[0] not in community[rep_name]:
                    community[rep_name][temp[0]] = {}
                if threshold not in community[rep_name][temp[0]]:
                    community[rep_name][temp[0]][threshold] = []
                community[rep_name][temp[0]][threshold].append(
                    (float(temp[4]), float(temp[5])))
        input.close()

    for rep in replicates:
        count_name = rep.split('/')[1].split('_')[0] + '_' + \
            rep.split('/')[1].split('_')[1]
        regions = community[count_name].keys()
        for region in regions:
            thresholds = community[count_name][region].keys()
            for threshold in thresholds:
                counts = load_counts(str(rep))[region]
                plot_heatmap(counts,
                             'output/heatmaps/' + count_name + '_' + region +
                             "_variance_" + str(threshold) + '.png',
                             colorscale=colorscale['obs'][region],
                             show_colorscale=True, cmap=scale, region=region,
                             communities=community[count_name][region][
                                 threshold],
                             primer_file=glob.glob('input/*.bed')[0])


if __name__ == "__main__":
    main()
    # main_communities()
