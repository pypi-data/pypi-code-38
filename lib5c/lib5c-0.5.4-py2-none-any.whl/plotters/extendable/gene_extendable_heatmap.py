"""
Module for the GeneExtendableHeatmap class, which adds gene track plotting
functionality for the extendable heatmap system.
"""

import os

import matplotlib.collections as collections
from matplotlib.colors import to_rgba

from lib5c.plotters.extendable import BaseExtendableHeatmap
from lib5c.parsers.genes import load_gene_table
from lib5c.util.bed import check_intersect


class GeneExtendableHeatmap(BaseExtendableHeatmap):
    """
    ExtendableHeatmap mixin class providing gene track plotting functionality.

    To deal with the fact that genes may overlap (e.g., where a gene has
    multiple isoforms), this class uses the concept of "gene stacks". Each gene
    track in a gene stack represents a separate axis added to the
    ExtendableHeatmap. By packing a set of genes into separate "rows", functions
    like ``add_gene_stack()`` can plot each row in the stack as a separate gene
    track via ``add_gene_track()``.

    Most commonly, we will want to add reference gene tracks corresponding to a
    particular genome assembly. To make this easy, this class provides the
    ``add_refgene_stack()`` and ``add_refgene_stacks()`` functions.
    """
    def add_gene_tracks(self, genes, size='3%', pad=0.0, axis_limits=(0, 1),
                        intron_height=0.05, exon_height=0.5, colors=None):
        """
        Adds a gene track for a single row of genes to both the bottom and
        left side of the heatmap by calling ``add_gene_track()`` twice.

        Parameters
        ----------
        genes : list of dict
            Each dict should represent a gene and could have the following
            keys::

                {
                    'chrom' : str,
                    'start' : int,
                    'end'   : int,
                    'name'  : str,
                    'id'    : str,
                    'strand': '+' or '-',
                    'blocks': list of dicts
                }

            Each block represents an exon  as dicts with the following
            structure::

                {
                    'start': int,
                    'end'  : int
                }

            The 'name' and 'id' keys are optional and are only used when color-
            coding genes. See ``lib5c.parsers.genes.load_genes()``.
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        axis_limits : tuple of float
            Axis limits for the non-genomic axis of the gene track.
        intron_height : float
            Controls thickness of gene introns. Pass a larger number for thicker
            introns.
        exon_height : float
            Controls thickness of gene exons. Pass a larger number for thicker
            exons.
        colors : dict, optional
            Pass a dict mapping gene names or id's to matplotlib colors to color
            code those genes. Genes not in the dict will be colored black by
            default. Using gene names as keys should color all isoforms, while
            using gene id's as keys should color just the isoform matching the
            specified id.

        Returns
        -------
        list of pyplot axes
            The newly added gene track axes.
        """
        ax_h = self.add_gene_track(
            genes, loc='bottom', size=size, pad=pad, new_ax_name='h_genes',
            axis_limits=axis_limits, intron_height=intron_height,
            exon_height=exon_height, colors=colors)
        ax_v = self.add_gene_track(
            genes, loc='left', size=size, pad=pad, new_ax_name='v_genes',
            axis_limits=axis_limits, intron_height=intron_height,
            exon_height=exon_height, colors=colors)
        return [ax_h, ax_v]

    def add_gene_track(self, genes, loc='bottom', size='3%', pad=0.0,
                       new_ax_name='genes', axis_limits=(0, 1),
                       intron_height=0.05, exon_height=0.5, colors=None):
        """
        Adds one gene track (for one row of genes) along either the x- or y-axis
        of the heatmap.

        Parameters
        ----------
        genes : list of dict
            Each dict should represent a gene and could have the following
            keys::

                {
                    'chrom' : str,
                    'start' : int,
                    'end'   : int,
                    'name'  : str,
                    'id'    : str,
                    'strand': '+' or '-',
                    'blocks': list of dicts
                }

            Each block represents an exon  as dicts with the following
            structure::

                {
                    'start': int,
                    'end'  : int
                }

            The 'name' and 'id' keys are optional and are only used when color-
            coding genes. See ``lib5c.parsers.genes.load_genes()``.
        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the heatmap to add the new gene track to.
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        new_ax_name : str
            The name for the new axis. You can access the new axis later at
            ``h[name]`` where ``h`` is this ExtendableHeatmap instance.
        axis_limits : tuple of float
            Axis limits for the non-genomic axis of the gene track.
        intron_height : float
            Controls thickness of gene introns. Pass a larger number for thicker
            introns.
        exon_height : float
            Controls thickness of gene exons. Pass a larger number for thicker
            exons.
        colors : dict, optional
            Pass a dict mapping gene names or id's to matplotlib colors to color
            code those genes. Genes not in the dict will be colored black by
            default. Using gene names as keys should color all isoforms, while
            using gene id's as keys should color just the isoform matching the
            specified id.

        Returns
        -------
        pyplot axis
            The newly added gene track axis.
        """
        # create new axis
        ax = self.add_margin_ax(loc=loc, size=size, pad=pad,
                                new_ax_name=new_ax_name,
                                axis_limits=axis_limits)

        # deduce orientation, either h or v, and save the correct grange
        if loc in ['bottom', 'top']:
            orientation = 'horizontal'
            grange = self.grange_x
        else:
            orientation = 'vertical'
            grange = self.grange_y

        # deduce midpoint of the non-genomic axis
        midpoint = (axis_limits[0] + axis_limits[1]) / 2.

        # compute track_width and track_height, assuming horizontal orientation
        track_width = grange['end'] - grange['start']
        track_height = abs(axis_limits[1] - axis_limits[0])

        # create patches for each gene
        verts = []
        polycolors = []
        segments = []
        linecolors = []
        for gene in genes:
            # skip genes that don't intersect the window
            if not check_intersect(gene, grange):
                continue

            # determine color for this gene
            color = to_rgba('k')
            if colors is not None:
                if gene['id'] in colors:
                    color = to_rgba(colors[gene['id']])
                elif gene['name'] in colors:
                    color = to_rgba(colors[gene['name']])

            # plot intron rectangle
            l, r, t, b = (gene['start'], gene['end'],
                          midpoint + intron_height / 2.,
                          midpoint - intron_height / 2.)
            hverts = [(l, b), (r, b), (r, t), (l, t)]
            if orientation == 'vertical':
                verts.append([(y, x) for x, y in hverts])
            else:
                verts.append(hverts)
            polycolors.append(color)

            # plot exon rectangles
            for block in gene['blocks']:
                l, r, t, b = (block['start'], block['end'],
                              midpoint + exon_height / 2.,
                              midpoint - exon_height / 2.)
                hverts = [(l, b), (r, b), (r, t), (l, t)]
                if orientation == 'vertical':
                    verts.append([(y, x) for x, y in hverts])
                else:
                    verts.append(hverts)
                polycolors.append(color)

            # plot a little arrow based on the strand information if present
            # TODO: figure out why this factor of 40 is necessary
            arrow_size = (exon_height / 60.) * (track_width / track_height)
            if gene['strand'] == '+':
                upper_coords = [
                    (gene['start'], midpoint),
                    (gene['start'] - arrow_size, midpoint + exon_height / 2.)
                ]
                lower_coords = [
                    (gene['start'], midpoint),
                    (gene['start'] - arrow_size, midpoint - exon_height / 2.)
                ]
            elif gene['strand'] == '-':
                upper_coords = [
                    (gene['end'], midpoint),
                    (gene['end'] + arrow_size, midpoint + exon_height / 2.)
                ]
                lower_coords = [
                    (gene['end'], midpoint),
                    (gene['end'] + arrow_size, midpoint - exon_height / 2.)
                ]
            else:
                continue
            if orientation == 'vertical':
                upper_coords = [(y, x) for x, y in upper_coords]
                lower_coords = [(y, x) for x, y in lower_coords]
            segments.append(upper_coords)
            linecolors.append(color)
            segments.append(lower_coords)
            linecolors.append(color)

        ax.add_collection(
            collections.LineCollection(segments, colors=linecolors))
        ax.add_collection(
            collections.PolyCollection(verts, edgecolors=polycolors,
                                       facecolors=polycolors))

        return ax

    def add_gene_stacks(self, genes, size='3%', pad_before=0.0, pad_within=0.0,
                        axis_limits=(0, 1), intron_height=0.05, exon_height=0.5,
                        padding=1000, colors=None):
        """
        Adds a gene stack for a set of genes to both the bottom and left side of
        the heatmap by calling ``add_gene_stack()`` twice.

        Parameters
        ----------
        genes : list of dict
            Each dict should represent a gene and could have the following
            keys::

                {
                    'chrom' : str,
                    'start' : int,
                    'end'   : int,
                    'name'  : str,
                    'id'    : str,
                    'strand': '+' or '-',
                    'blocks': list of dicts
                }

            Each block represents an exon  as dicts with the following
            structure::

                {
                    'start': int,
                    'end'  : int
                }

            The 'name' and 'id' keys are optional and are only used when color-
            coding genes. See ``lib5c.parsers.genes.load_genes()``.
        size : str
            The size of each new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad_before : float
            The padding to use between the existing parts of the figure and the
            newly added gene tracks.
        pad_within : float
            The padding to use between each newly added gene track.
        axis_limits : tuple of float
            Axis limits for the non-genomic axis of each new gene track.
        intron_height : float
            Controls thickness of gene introns. Pass a larger number for thicker
            introns.
        exon_height : float
            Controls thickness of gene exons. Pass a larger number for thicker
            exons.
        padding : int
            The padding to use when packing genes into rows, in units of base
            pairs. Genes that are within this many base pairs of each other will
            get packed into different rows.
        colors : dict, optional
            Pass a dict mapping gene names or id's to matplotlib colors to color
            code those genes. Genes not in the dict will be colored black by
            default. Using gene names as keys should color all isoforms, while
            using gene id's as keys should color just the isoform matching the
            specified id.

        Returns
        -------
        list of lists of pyplot axis
            The first element of the outer list is a list of the newly added
            horizontal gene track axes, one for each row of genes. The second
            element is the same but for the newly added vertical gene track
            axes.
        """
        ax_hs = self.add_gene_stack(
            genes, loc='bottom', size=size, pad_before=pad_before,
            pad_within=pad_within, axis_limits=axis_limits,
            intron_height=intron_height, exon_height=exon_height,
            padding=padding, colors=colors)
        ax_vs = self.add_gene_stack(
            genes, loc='left', size=size, pad_before=pad_before,
            pad_within=pad_within, axis_limits=axis_limits,
            intron_height=intron_height, exon_height=exon_height,
            padding=padding, colors=colors)
        return [ax_hs, ax_vs]

    def add_gene_stack(self, genes, loc='bottom', size='3%', pad_before=0.0,
                       pad_within=0.0, axis_limits=(0, 1), intron_height=0.05,
                       exon_height=0.5, padding=1000, colors=None):
        """
        Adds one stack of gene tracks along either the x- or y-axis of the
        heatmap by packing one set of genes into rows and calling
        ``add_gene_track()`` once for every row.

        Parameters
        ----------
        genes : list of dict
            Each dict should represent a gene and could have the following
            keys::

                {
                    'chrom' : str,
                    'start' : int,
                    'end'   : int,
                    'name'  : str,
                    'id'    : str,
                    'strand': '+' or '-',
                    'blocks': list of dicts
                }

            Each block represents an exon  as dicts with the following
            structure::

                {
                    'start': int,
                    'end'  : int
                }

            The 'name' and 'id' keys are optional and are only used when color-
            coding genes. See ``lib5c.parsers.genes.load_genes()``.
        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the heatmap to add the new gene tracks to.
        size : str
            The size of each new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad_before : float
            The padding to use between the existing parts of the figure and the
            newly added gene tracks.
        pad_within : float
            The padding to use between each newly added gene track.
        axis_limits : tuple of float
            Axis limits for the non-genomic axis of each new gene track.
        intron_height : float
            Controls thickness of gene introns. Pass a larger number for thicker
            introns.
        exon_height : float
            Controls thickness of gene exons. Pass a larger number for thicker
            exons.
        padding : int
            The padding to use when packing genes into rows, in units of base
            pairs. Genes that are within this many base pairs of each other will
            get packed into different rows.
        colors : dict, optional
            Pass a dict mapping gene names or id's to matplotlib colors to color
            code those genes. Genes not in the dict will be colored black by
            default. Using gene names as keys should color all isoforms, while
            using gene id's as keys should color just the isoform matching the
            specified id.

        Returns
        -------
        list of pyplot axis
            The newly added gene track axes, one for each row of genes.
        """
        # deduce orientation, either h or v, and save the correct grange
        if loc in ['bottom', 'top']:
            orientation = 'horizontal'
            grange = self.grange_x
        else:
            orientation = 'vertical'
            grange = self.grange_y

        # initialize data structures for packing
        row_cursors = []
        rows = []

        # initialize the first row
        rows.append([])
        row_cursors.append(-10000)  # basically should be -Inf

        # main loop for packing genes
        for gene in genes:
            # skip genes that don't intersect the window
            if not check_intersect(gene, grange):
                continue

            gene_placed = False
            for i in range(len(rows)):
                if gene['start'] > row_cursors[i] + padding:
                    row_cursors[i] = gene['end']
                    rows[i].append(gene)
                    gene_placed = True
                    break
            if not gene_placed:
                rows.append([gene])
                row_cursors.append(gene['end'])

        # add a track for each row
        return [
            self.add_gene_track(
                rows[i], loc=loc, size=size,
                pad=pad_before if i == 0 else pad_within,
                axis_limits=axis_limits, intron_height=intron_height,
                exon_height=exon_height,
                new_ax_name='%s_gene_track_%i' % (orientation, i),
                colors=colors)
            for i in range(len(rows))
        ]

    def add_refgene_stacks(self, assembly, size='3%', pad_before=0.0,
                           pad_within=0.0, axis_limits=(0, 1),
                           intron_height=0.05, exon_height=0.5, padding=1000,
                           colors=None):
        """
        Adds a gene stack for a set of genes to both the bottom and left side of
        the heatmap by calling ``add_refgene_stack()`` twice.

        Parameters
        ----------
        assembly : {'hg18', 'hg19', 'hg38', 'mm9', 'mm10'}
            The genome assembly to load reference genes for.
        size : str
            The size of each new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad_before : float
            The padding to use between the existing parts of the figure and the
            newly added gene tracks.
        pad_within : float
            The padding to use between each newly added gene track.
        axis_limits : tuple of float
            Axis limits for the non-genomic axis of each new gene track.
        intron_height : float
            Controls thickness of gene introns. Pass a larger number for thicker
            introns.
        exon_height : float
            Controls thickness of gene exons. Pass a larger number for thicker
            exons.
        padding : int
            The padding to use when packing genes into rows, in units of base
            pairs. Genes that are within this many base pairs of each other will
            get packed into different rows.
        colors : dict, optional
            Pass a dict mapping gene names or id's to matplotlib colors to color
            code those genes. Genes not in the dict will be colored black by
            default. Using gene names as keys should color all isoforms, while
            using gene id's as keys should color just the isoform matching the
            specified id.

        Returns
        -------
        list of lists of pyplot axis
            The first element of the outer list is a list of the newly added
            horizontal gene track axes, one for each row of genes. The second
            element is the same but for the newly added vertical gene track
            axes.
        """
        ax_hs = self.add_refgene_stack(
            assembly, loc='bottom', size=size, pad_before=pad_before,
            pad_within=pad_within, axis_limits=axis_limits,
            intron_height=intron_height, exon_height=exon_height,
            padding=padding, colors=colors)
        ax_vs = self.add_refgene_stack(
            assembly, loc='left', size=size, pad_before=pad_before,
            pad_within=pad_within, axis_limits=axis_limits,
            intron_height=intron_height, exon_height=exon_height,
            padding=padding, colors=colors)
        return [ax_hs, ax_vs]

    def add_refgene_stack(self, assembly, loc='bottom', size='3%',
                          pad_before=0.0, pad_within=0.0, axis_limits=(0, 1),
                          intron_height=0.05, exon_height=0.5, padding=1000,
                          colors=None):
        """
        Adds a gene stack to either the x- or y-axis of the heatmap by getting a
        set of reference genes for a specified genome assembly, and then passes
        that set of genes to ``add_gene_stack()``.

        Parameters
        ----------
        assembly : {'hg18', 'hg19', 'hg38', 'mm9', 'mm10'}
            The genome assembly to load reference genes for.
        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the heatmap to add the new gene tracks to.
        size : str
            The size of each new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad_before : float
            The padding to use between the existing parts of the figure and the
            newly added gene tracks.
        pad_within : float
            The padding to use between each newly added gene track.
        axis_limits : tuple of float
            Axis limits for the non-genomic axis of each new gene track.
        intron_height : float
            Controls thickness of gene introns. Pass a larger number for thicker
            introns.
        exon_height : float
            Controls thickness of gene exons. Pass a larger number for thicker
            exons.
        padding : int
            The padding to use when packing genes into rows, in units of base
            pairs. Genes that are within this many base pairs of each other will
            get packed into different rows.
        colors : dict, optional
            Pass a dict mapping gene names or id's to matplotlib colors to color
            code those genes. Genes not in the dict will be colored black by
            default. Using gene names as keys should color all isoforms, while
            using gene id's as keys should color just the isoform matching the
            specified id.

        Returns
        -------
        list of pyplot axis
            The newly added gene track axes, one for each row of genes.
        """
        if assembly not in ['hg18', 'hg19', 'hg38', 'mm9', 'mm10']:
            raise ValueError('unrecognized assembly %s' % assembly)
        directory, filename = os.path.split(__file__)
        if not directory:
            directory = '.'
        refgene_file_name = '%d/../gene_tracks/%g_refseq_genes.gz' \
            .replace('%d', directory) \
            .replace('%g', assembly) \
            .replace('%c', self.grange_x['chrom'])
        genes = load_gene_table(refgene_file_name)[self.grange_x['chrom']]

        return self.add_gene_stack(genes, loc=loc, size=size,
                                   pad_before=pad_before,
                                   pad_within=pad_within,
                                   axis_limits=axis_limits,
                                   intron_height=intron_height,
                                   exon_height=exon_height, padding=padding,
                                   colors=colors)
