from lib5c.plotters.extendable import ChipSeqExtendableHeatmap,\
    DomainExtendableHeatmap, GeneExtendableHeatmap, LegendExtendableHeatmap,\
    RulerExtendableHeatmap, ClusterExtendableHeatmap, SNPExtendableHeatmap,\
    MotifExtendableHeatmap, RectangleExtendableHeatmap, BedExtendableHeatmap,\
    BaseExtendableHeatmap


class ExtendableHeatmap(ChipSeqExtendableHeatmap, DomainExtendableHeatmap,
                        GeneExtendableHeatmap, LegendExtendableHeatmap,
                        RulerExtendableHeatmap, ClusterExtendableHeatmap,
                        SNPExtendableHeatmap, MotifExtendableHeatmap,
                        RectangleExtendableHeatmap, BedExtendableHeatmap,
                        BaseExtendableHeatmap):
    """
    Fully-extended ExtendableHeatmap class. Inherits from BaseExtendableHeatmap
    as well as all feature-providing classes.

    Examples
    --------
    >>> import numpy as np
    >>> import matplotlib.patches as patches
    >>> import matplotlib.colors as colors
    >>> from lib5c.parsers.counts import load_counts
    >>> from lib5c.parsers.primers import load_primermap
    >>> from lib5c.parsers.bed import load_features
    >>> from lib5c.parsers.table import load_table
    >>> from lib5c.plotters.extendable import ExtendableHeatmap
    >>> primermap = load_primermap('test/bins.bed')
    >>> counts = load_counts('test/test.counts', primermap)['Sox2']
    >>> h = ExtendableHeatmap(
    ...     array=counts,
    ...     grange_x={'chrom': 'chr3', 'start': 34108879, 'end': 35104879},
    ...     colorscale=(-10, 10),
    ...     colormap='obs_over_exp',
    ...     norm=colors.SymLogNorm(linthresh=0.03, linscale=0.03)
    ... )
    >>> xs = np.arange(len(counts)) + 0.5
    >>> h.add_rulers()
    [<matplotlib.axes._axes.Axes object at ...>,
     <matplotlib.axes._axes.Axes object at ...>]
    >>> h.add_refgene_stacks('mm9', pad_before=0.1,
    ...                      colors={'NM_011443': 'r', 'NR_015580': 'b'})
    [[<matplotlib.axes._axes.Axes object at ...>,
      <matplotlib.axes._axes.Axes object at ...>],
     [<matplotlib.axes._axes.Axes object at ...>,
      <matplotlib.axes._axes.Axes object at ...>]]
    >>> h.add_legend({'Sox2': 'red', 'Sox2 OT': 'blue'})
    <matplotlib.legend.Legend object at ...>
    >>> boundaries = [{'chrom': 'chr3', 'start': 34459302, 'end': 34576915}]
    >>> h.add_chipseq_tracks(load_features('test/tracks/CTCF_ES.bed',
    ...                                    boundaries=boundaries)['chr3'],
    ...                      name='ES CTCF')
    [<matplotlib.axes._axes.Axes object at ...,
     <matplotlib.axes._axes.Axes object at ...>]
    >>> h.add_chipseq_tracks(load_features('test/tracks/CTCF_NPC.bed',
    ...                                    boundaries=boundaries)['chr3'],
    ...                      name='NPC CTCF', color='r')
    [<matplotlib.axes._axes.Axes object at ...,
     <matplotlib.axes._axes.Axes object at ...>]
    >>> h.add_ax('sin')
    <matplotlib.axes._axes.Axes object at ...>
    >>> h['sin'].plot(xs, np.sin(xs))
    [<matplotlib.lines.Line2D object at ...>]
    >>> h['sin'].set_xlim((0, len(counts)))
    (0, 83)
    >>> h.add_colorbar()
    <matplotlib.colorbar.Colorbar object at ...>
    >>> h['horizontal_gene_track_1'].text(34558297, 0.5, 'Sox2', va='center',
    ...                                   ha='left', fontsize=5, color='r')
    Text(3.45583e+07,0.5,'Sox2')
    >>> h['horizontal_gene_track_1'].add_patch(
    ...     patches.Rectangle([34541337, 0], 16960, 1, fill=False, ec='r')
    ... )
    <matplotlib.patches.Rectangle object at ...>
    >>> h.outline_domains(load_features('test/communities.bed')['chr3'])
    >>> h.add_clusters(
    ...     load_table('test/colors.tsv', load_primermap('test/bins_new.bed'),
    ...                dtype='|S25')['x']['Sox2'][0:41, 0:41],
    ...     colors='random')
    >>> h.add_rectangles(['chr3:34541337-34568297_chr3:34651337-34678297'])
    >>> h.add_rectangles(['chr3:34541337-34568297_chr3:34651337-34678297'],
    ...                  color='red', transpose=False)
    >>> h.save('test/extendableheatmap.png')
    """
    pass
