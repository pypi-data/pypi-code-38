"""Plotting for data-objects"""
# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>

from ._base import reset_rc
from ._colors import (
    ColorBar, ColorGrid, ColorList,
    colors_for_categorial, colors_for_oneway, colors_for_twoway,
    single_hue_colormap,
)
from ._figure import Figure
from ._glassbrain import GlassBrain
from ._line import LineStack
from ._sensors import SensorMaps, SensorMap
from ._topo import TopoArray, TopoButterfly, Topomap, TopomapBins
from ._uts import UTSStat, UTS, UTSClusters
from ._utsnd import Array, Butterfly
from ._uv import (
    Barplot, Boxplot, Correlation, Histogram, PairwiseLegend, Regression,
    Timeplot,
)
from . import brain
