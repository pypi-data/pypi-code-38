"""
Module for the ClusterExtendableHeatmap class, which adds cluster outlining
functionality for the extendable heatmap system.
"""

import numpy as np
from matplotlib import cm

from lib5c.plotters.extendable import BaseExtendableHeatmap
from lib5c.algorithms.clustering.util import reshape_cluster_array_to_dict,\
    center_of_mass, belongs_to


class ClusterExtendableHeatmap(BaseExtendableHeatmap):
    """
    ExtendableHeatmap mixin class providing cluster outlining functionality.
    """
    def add_clusters(self, cluster_array, colors=None, weight='100x',
                     outline_color=None, outline_weight='2x', labels=None,
                     fontsize=7):
        """
        Adds clusters to the heatmap surface.

        Parameters
        ----------
        cluster_array: np.ndarray
            Array of cluster IDs. Should match size and shape of the underlying
            array this ExtendableHeatmap was constructed with.
        colors: 'random' or single color or list/dict of colors or None
            Pass 'random' for random colors, pass a dict mapping cluster IDs to
            matplotlib colors to outline each cluster in the indicated color,
            pass None to skip outlining clusters.
        weight : numeric or str
            Pass a numeric to set the linewidth for the cluster outlines. Pass a
            string ending in "x" (such as "100x") to specify the line width as a
            multiple of the inverse of the number of pixels in the heatmap.
        outline_color : matplotlib color or None
            Pass a matplotlib color to outline the outlines (e.g. with neon
            green) to make them stand out more. Pass None to skip adding this
            extra outline.
        outline_weight : numeric or str
            ass a numeric to set the linewidth for the outlines of the cluster
            outlines. Pass a string ending in "x" (such as "2x") to specify the
            line width as a multiple of the outline linewidth.
        labels : True, dict of str, or None
            Pass True to simply label the clusters by their ID. Pass a mapping
            from cluster IDs to labels to label the clusters with a the labels.
            Pass None to skip outlining clusters.
        fontsize : numeric
            The font size to use for cluster labels.
        """
        clusters = reshape_cluster_array_to_dict(cluster_array)
        if colors:
            # resolve line width
            base_linewidth = weight
            if type(weight) == str:
                base_linewidth = float(weight[:-1]) / len(self.array)

            # resolve outline line width
            outline_linewidth = base_linewidth * 2
            if outline_color is not None and outline_weight is not None:
                if type(outline_weight) == str:
                    outline_linewidth = float(
                        outline_weight[:-1]) * base_linewidth
                else:
                    outline_linewidth = base_linewidth + outline_weight

            # resolve colors
            if colors is None:
                pass
            elif colors == 'random':
                color_multiplier = 256 / max(len(clusters) - 1, 1)
                cluster_ids = clusters.keys()
                colors = {cluster_ids[i]: cm.gist_ncar(i * color_multiplier)
                          for i in range(len(cluster_ids))}
            elif type(colors) not in [dict, list]:
                colors = {cluster_id: colors for cluster_id in clusters}

            # resolve labels
            if labels is True:
                labels = {cluster_id: cluster_id for cluster_id in clusters}

            # add outlines of the outlines first
            if outline_color is not None:
                for cluster_id in clusters:
                    self.outline_cluster(clusters[cluster_id], outline_color,
                                         linewidth=outline_linewidth)

            # outline clusters
            if colors is not None:
                for cluster_id in clusters:
                    self.outline_cluster(clusters[cluster_id],
                                         colors[cluster_id],
                                         linewidth=base_linewidth)

            # label clusters
            if labels is not None:
                for cluster_id in clusters:
                    self.label_cluster(clusters[cluster_id], labels[cluster_id],
                                       fontsize=fontsize)

    def outline_cluster(self, cluster, color, linewidth=2):
        """
        Outlines a single cluster in the specified color.

        Parameters
        ----------
        cluster : list of {'x': int, 'y': int} dicts
            The cluster to outline.
        color : matplotlib color
            The color to outline in.
        linewidth : numeric
            The linewidth to use.
        """
        # reference to axis to plot to
        ax = self['root']

        for peak in cluster:
            # top
            query_peak = {'x': peak['x'], 'y': peak['y'] - 1}
            if not belongs_to(query_peak, cluster):
                x = peak['x']
                y = peak['y']
                ax.plot([x, x + 1], [y, y], c=color, lw=linewidth)

            # bottom
            query_peak = {'x': peak['x'], 'y': peak['y'] + 1}
            if not belongs_to(query_peak, cluster):
                x = peak['x']
                y = peak['y']
                ax.plot([x, x + 1], [y + 1, y + 1], c=color, lw=linewidth)

            # left
            query_peak = {'x': peak['x'] - 1, 'y': peak['y']}
            if not belongs_to(query_peak, cluster):
                x = peak['x']
                y = peak['y']
                ax.plot([x, x], [y, y + 1], c=color, lw=linewidth)

            # right
            query_peak = {'x': peak['x'] + 1, 'y': peak['y']}
            if not belongs_to(query_peak, cluster):
                x = peak['x']
                y = peak['y']
                ax.plot([x + 1, x + 1], [y, y + 1], c=color, lw=linewidth)

    def label_cluster(self, cluster, label, fontsize=7):
        """
        Labels a cluster.

        Parameters
        ----------
        cluster : list of {'x': int, 'y': int} dicts
            The cluster to label.
        label : str
            The string to label the cluster with.
        fontsize : numeric
            The fontsize to use for the label.
        """
        centroid = center_of_mass(cluster) + np.array([0.5, 0.5])
        self['root'].text(centroid[0], centroid[1], str(label),
                          fontsize=fontsize, ha='center', va='center')
