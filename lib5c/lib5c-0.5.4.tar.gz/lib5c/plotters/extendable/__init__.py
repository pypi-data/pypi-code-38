"""
Module describing the extendable heatmap plotting system.

The core idea behind this system is the ExtendableFigure API. Subclasses of
ExtendableFigure inherit the ``add_ax()`` instance method, which tacks on
additional matplotlib axes to an existing axis using a ``divider`` object
obtained using the matplotlib function
``mpl_toolkits.axes_grid1.make_axes_locatable()``. The new axes are stored in
an ``axes`` dict instance variable on the ExtendableFigure and can subsequently
be plotted on with any matplotlib-based function.

This means that an arbitrary number of additional data tracks can be added to
the ExtendableFigure in a sequential, interactive manner.

The BaseExtendableHeatmap class extends ExtendableFigure and implements extra
functionality specific for plotting contact frequency heatmaps. This includes a
custom interface to ``add_ax()`` called ``add_margin_ax()``, designed to make it
easy to add tracks to the margins of a contact frequency heatmap.

In order to handle the wide diversity of tracks and overlays that may be added
to a contact frequency heatmap, a wide variety of plug-in mixin classes are
defined. These mixin classes each implement one specific feature in the form of
a few related instance methods that internally call ``add_margin_ax()``. For
example, ChipSeqExtendableHeatmap provides a function ``add_chipseq_track()``
which uses ``add_margin_ax()`` to add a ChIP-seq track to the ExtendableHeatmap.
The separation of different features into separate mixin classes makes the code
easier to understand and also makes it easy to add new features.

The feature functions like ``add_chipseq_track()`` typically accept some data as
well as parameters for creating the new axis. The functions typically create the
new axis using ``add_margin_ax()``, passing through the relevant parameters. The
functions then plot the data to the newly created axis using matplotlib plotting
functions. Finally, they return the new axis.

By convention, we often plot tracks on both the left and the bottom of the
heatmap. To make this easier, most feature functions like
``add_chipseq_track()`` have associated helper functions like
``add_chipseq_tracks()``, which simply calls ``add_chipseq_track()`` twice: once
with ``loc='bottom'`` and once with ``loc='left'``.

To add a new feature:

 1. create a new mixin class extending BaseExtendableHeatmap that implements the
    functions for your feature,
 2. place your new class in the ``lib5c.plotters.extendable`` module,
 3. import your class in the top level module file ``__init__.py`` and add it to
    the ``__all__`` variable, and
 4. add your class to the list of classes inherited by ExtendableHeatmap, making
    sure to place it before BaseExtendableHeatmap in the list.

In the future, this process may be automated.
"""

from lib5c.plotters.extendable.extendable_figure import \
    ExtendableFigure
from lib5c.plotters.extendable.base_extendable_heatmap import \
    BaseExtendableHeatmap
from lib5c.plotters.extendable.chipseq_extendable_heatmap import \
    ChipSeqExtendableHeatmap
from lib5c.plotters.extendable.domain_extendable_heatmap import \
    DomainExtendableHeatmap
from lib5c.plotters.extendable.gene_extendable_heatmap import \
    GeneExtendableHeatmap
from lib5c.plotters.extendable.legend_extendable_heatmap import \
    LegendExtendableHeatmap
from lib5c.plotters.extendable.cluster_extendable_heatmap import \
    ClusterExtendableHeatmap
from lib5c.plotters.extendable.ruler_extendable_heatmap import \
    RulerExtendableHeatmap
from lib5c.plotters.extendable.snp_extendable_heatmap import \
    SNPExtendableHeatmap
from lib5c.plotters.extendable.motif_extendable_heatmap import \
    MotifExtendableHeatmap
from lib5c.plotters.extendable.rectangle_extendable_heatmap import \
    RectangleExtendableHeatmap
from lib5c.plotters.extendable.bed_extendable_heatmap import \
    BedExtendableHeatmap
from lib5c.plotters.extendable.extendable_heatmap import \
    ExtendableHeatmap

__all__ = [
    'ExtendableFigure',
    'BaseExtendableHeatmap',
    'ChipSeqExtendableHeatmap',
    'DomainExtendableHeatmap',
    'GeneExtendableHeatmap',
    'LegendExtendableHeatmap',
    'ClusterExtendableHeatmap',
    'RulerExtendableHeatmap',
    'SNPExtendableHeatmap',
    'MotifExtendableHeatmap',
    'RectangleExtendableHeatmap',
    'BedExtendableHeatmap',
    'ExtendableHeatmap'
]
