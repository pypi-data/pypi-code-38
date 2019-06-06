"""
Module providing ``plot_heatmap()``, a wrapper function for the extendable
heatmap system defined in the ``lib5c.plotters.extendable`` module.
"""

import os
import itertools
import warnings

from lib5c.parsers.bed import load_features
from lib5c.plotters.extendable import ExtendableHeatmap
from lib5c.util.plotting import plotter
from lib5c.util.parallelization import parallelize_regions
from lib5c.contrib.pybigwig.bigwig import bigwig_avail, BigWig


@parallelize_regions
@plotter
def plot_heatmap(matrix, grange_x, grange_y=None, rulers=True, ruler_fontsize=7,
                 genes=None, gene_colors=None, colorscale=None, colorbar=False,
                 colormap='abs_obs', motif_tracks=None, motif_track_colors=None,
                 motif_track_labels=None, motif_linewidth=0.5, bed_tracks=None,
                 bed_track_colors=None, bed_track_labels=None,
                 chipseq_tracks=None, snp_tracks=None, snp_colors=None,
                 snp_track_labels=None, chipseq_track_scales=None,
                 chipseq_track_colors=None, chipseq_track_labels=None,
                 domains=None, domain_color='g', clusters=None,
                 cluster_colors=None, dpi=800, despine=False, style=None,
                 **kwargs):
    """
    Wrapper function for creating ExtendableHeatmaps.

    Parameters
    ----------
    matrix : np.ndarray
        The matrix to plot in the heatmap.
    grange_x : dict or list of dict
        The genomic range represented by the x-axis of this heatmap. The dict
        should have the form::

            {
                'chrom': str,
                'start': int,
                'end': int
            }

        Pass a list of dicts of this form (assumed to be sorted) to assume that
        the genomic range extends from the start of the first range to the end
        of the last range.
    grange_y : dict, optional
        The genomic range represented by the y-axis of this heatmap. If None,
        the heatmap is assumed to be symmetric.
    rulers : bool
        Pass True to include genomic coordinate rulers on the heatmap.
    ruler_fontsize : int
        Controls the fontsize for the ruler when ``rulers`` is True.
    genes : str or list of dict
        Pass None to skip plotting gene tracks. Pass one of 'mm9', 'mm10',
        'hg18', 'hg19', or 'hg38' to add gene tracks for the selected reference
        genome. To plot a custom set of genes, pass a list of dicts of the
        form::

            {
                'chrom' : str,
                'start' : int,
                'end'   : int,
                'name'  : str,
                'strand': '+' or '-',
                'blocks': list of dicts
            }

        Blocks typically represent exons and are represented as dicts with the
        following structure::

            {
                'start': int,
                'end'  : int
            }

    gene_colors : dict, optional
        Pass a dict mapping gene names or ID's as strings to valid matplotlib
        colors to plot specific genes in the specified colors.
    colorscale : tuple of float, optional
        Specify the range of the heatmap colorbar as a tuple of the form
        (min, max).
    colorbar : bool
        Pass True to include a colorbar.
    colormap : str
        Specify the colormap to use.
    motif_tracks : list of str, optional
        Pass file references to bed files to add to the heatmap as motif tracks.
    motif_track_colors : dict, optional
        Map from strand value (e.g., '+', '-') to color name for motifs with
        that strand value (i.e., orientation). If not provided for a given
        strand, color is 'k' by default.
    motif_track_labels : list of str, optional
        Parallel to ``motif_tracks``, the ith string will be used to label the
        ith motif track.
    motif_linewidth : float
        Pass a linewidth to use when drawing motif instances.
    bed_tracks : list of str, optional
        Pass file references to bed files to add to the heatmap as bed tracks.
    bed_track_colors : dict, optional
        Map from strand value (e.g., '+', '-') to color name for bed features
        with that strand value (i.e., orientation). If not provided for a given
        strand, color is 'k' by default.
    bed_track_labels : Parallel to ``bed_tracks``, the ith string will be used
        to label the ith bed track.
    snp_tracks : list of str, optional
        Pass file references to bed files to add to the heatmap as SNP tracks.
    snp_colors : dict, optional
        Map from SNP id's or names to colors. If not provided for a given SNP,
        color is 'k' by default.
    snp_track_labels : list of str, optional
        Parallel to ``snp_tracks``, the ith string will be used to label the ith
        SNP track.
    chipseq_tracks : list of str or list of lists of dicts, optional
        Pass file references to bed, bedgraph, or bigwig files to add to the
        heatmap as chipseq/feature tracks. Alternatively, pass a list of feature
        lists where each feature is a dict with the form::

            {
                'chrom': str,
                'start': int,
                'end': int,
                'value': float
            }

        where the 'value' key is optional.
    chipseq_track_scales : list of tuples of float, optional
        Parallel to ``chipseq_tracks``, the ith tuple should have the form
        (min, max) and should specify the axis limits of the ith track. Pass
        None to scale chipseq tracks automatically.
    chipseq_track_colors : list of str, optional
        Parallel to ``chipseq_tracks``, the ith string should indicate the color
        of the ith chipseq track. Pass None to color all chipseq tracks black.
    chipseq_track_labels : list of str, optional
        Parallel to ``chipseq_tracks``, the ith string will be used to label the
        ith chipseq track.
    domains : list of dict, optional
        Each dict should represent one domain and should have the form::

            {
                'chrom': str,
                'start': int,
                'end': int
            }

    domain_color : str
        The color to use to outline the domains.
    clusters : list of lists of dicts, optional
        Each inner list should describe one cluster to be outlined. Each cluster
        is a list of dicts of the form::

            {
                'x': int,
                'y': int
            }

        where these integers represent indices of ``matrix``.
    cluster_colors : list of str, optional
        Parallel to ``clusters``, the ith string should indicate the color to
        use to outline the ith cluster. Pass None to outline all clusters in
        green.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    lib5c.plotters.extendable.ExtendableHeatmap
        The resulting ExtendableHeatmap.
    """
    # handle case where grange_x is a list
    if type(grange_x) == list:
        grange_x = {'chrom': grange_x[0]['chrom'],
                    'start': grange_x[0]['start'],
                    'end': grange_x[-1]['end']}

    # make the basic heatmap object
    h = ExtendableHeatmap(
        array=matrix,
        grange_x=grange_x,
        grange_y=grange_y,
        colorscale=colorscale,
        colormap=colormap
    )

    # add rulers
    if rulers:
        h.add_rulers(fontsize=ruler_fontsize)

    # add snp tracks
    if snp_tracks is not None:
        padding = itertools.chain((0.1,), itertools.repeat(0.0))
        snps = [load_features(x) for x in snp_tracks]
        snp_names = [os.path.splitext(os.path.basename(x))[0]
                     for x in snp_tracks]
        for i, (snp_name, snp_track) in enumerate(zip(snp_names, snps)):
            track_label = snp_track_labels[i] \
                if snp_track_labels is not None else None
            h.add_snp_tracks(snp_track[grange_x['chrom']], name=snp_name,
                             pad=next(padding), colors=snp_colors,
                             track_label=track_label)

    # add gene tracks
    if genes is not None:
        if genes in ['mm9', 'mm10', 'hg18', 'hg19', 'hg38']:
            h.add_refgene_stacks(genes, colors=gene_colors)
        else:
            h.add_gene_stacks(genes, colors=gene_colors)

    # add chipseq tracks
    if chipseq_tracks is not None:
        # set default scales and colors if necessary
        if chipseq_track_scales is None:
            chipseq_track_scales = [None] * len(chipseq_tracks)
        if chipseq_track_colors is None:
            chipseq_track_colors = ['k'] * len(chipseq_tracks)

        # plot each track
        for i in range(len(chipseq_tracks)):
            # get a feature set based on the file extension
            ext = os.path.splitext(chipseq_tracks[i])[1].lower()
            if ext in ['.bw', '.bigwig']:
                if not bigwig_avail():
                    warnings.warn('failed to import pyBigWig - '
                                  'is it installed?', ImportWarning)
                    continue
                features_x = BigWig(chipseq_tracks[i]).query(
                    grange_x, num_bins=1000)
                features_y = BigWig(chipseq_tracks[i]).query(
                    grange_y, num_bins=1000)
            else:
                features_x = load_features(
                    chipseq_tracks[i], boundaries=[grange_x])[grange_x['chrom']]
                features_y = load_features(
                    chipseq_tracks[i], boundaries=[grange_y])[grange_y['chrom']]
            track_label = chipseq_track_labels[i] \
                if chipseq_track_labels is not None else None
            h.add_chipseq_track(
                features_x, loc='bottom', name=chipseq_tracks[i],
                axis_limits=chipseq_track_scales[i],
                color=chipseq_track_colors[i], track_label=track_label)
            h.add_chipseq_track(
                features_y, loc='left', name=chipseq_tracks[i],
                axis_limits=chipseq_track_scales[i],
                color=chipseq_track_colors[i], track_label=track_label)

    # add motif tracks
    if motif_tracks is not None:
        motifs = [load_features(x) for x in motif_tracks]
        motif_names = [os.path.splitext(os.path.basename(x))[0]
                       for x in motif_tracks]
        for i, (motif_name, motif) in enumerate(zip(motif_names, motifs)):
            track_label = motif_track_labels[i] \
                if motif_track_labels is not None else None
            h.add_motif_tracks(motif[grange_x['chrom']], name=motif_name,
                               motif_linewidth=motif_linewidth,
                               colors=motif_track_colors,
                               track_label=track_label)

    # add bed tracks
    if bed_tracks is not None:
        bed_features = [load_features(x) for x in bed_tracks]
        bed_names = [os.path.splitext(os.path.basename(x))[0]
                     for x in bed_tracks]
        for i, (bed_name, bed_feature) in enumerate(zip(bed_names,
                                                        bed_features)):
            track_label = bed_track_labels[i] \
                if bed_track_labels is not None else None
            h.add_bed_tracks(bed_feature[grange_x['chrom']], name=bed_name,
                             colors=bed_track_colors, track_label=track_label)

    # add domain outlines
    if domains is not None:
        h.outline_domains(domains, color=domain_color)

    # add cluster outlines
    if clusters is not None:
        if cluster_colors is None:
            cluster_colors = ['g'] * len(clusters)
        for i in range(len(clusters)):
            h.outline_cluster(clusters[i], cluster_colors[i])

    # add colorbar
    if colorbar:
        h.add_colorbar()

    return h
