from collections import Iterable

import Orange
import numpy as np
from Orange.data.util import SharedComputeValue
from Orange.preprocess.preprocess import Preprocess

try:  # get_unique_names was introduced in Orange 3.20
    from Orange.widgets.utils.annotated_data import get_next_name as get_unique_names
except ImportError:
    from Orange.data.util import get_unique_names

from AnyQt.QtCore import Qt

from orangecontrib.spectroscopy.data import getx
from orangecontrib.spectroscopy.preprocess.utils import nan_extend_edges_and_interpolate, CommonDomain, \
    edge_baseline

INTEGRATE_DRAW_CURVE_WIDTH = 2
INTEGRATE_DRAW_EDGE_WIDTH = 1
INTEGRATE_DRAW_BASELINE_PENARGS = {"width": INTEGRATE_DRAW_CURVE_WIDTH, "style": Qt.DotLine}
INTEGRATE_DRAW_CURVE_PENARGS = {"width": INTEGRATE_DRAW_CURVE_WIDTH}
INTEGRATE_DRAW_EDGE_PENARGS = {"width": INTEGRATE_DRAW_EDGE_WIDTH}


class IntegrateFeature(SharedComputeValue):

    def __init__(self, limits, commonfn):
        self.limits = limits
        super().__init__(commonfn)

    def baseline(self, data, common=None):
        if common is None:
            common = self.compute_shared(data)
        x_s, y_s = self.extract_data(data, common)
        return x_s, self.compute_baseline(x_s, y_s)

    def draw_info(self, data, common=None):
        if common is None:
            common = self.compute_shared(data)
        x_s, y_s = self.extract_data(data, common)
        return self.compute_draw_info(x_s, y_s)

    def extract_data(self, data, common):
        data, x, x_sorter = common
        # find limiting indices (inclusive left, exclusive right)
        lim_min, lim_max = min(self.limits), max(self.limits)
        lim_min = np.searchsorted(x, lim_min, sorter=x_sorter, side="left")
        lim_max = np.searchsorted(x, lim_max, sorter=x_sorter, side="right")
        x_s = x[x_sorter][lim_min:lim_max]
        y_s = data.X[:, x_sorter][:, lim_min:lim_max]
        return x_s, y_s

    def compute_draw_info(self, x_s, y_s):
        return {}

    @staticmethod
    def parameters():
        """ Return parameters for this type of integral """
        raise NotImplementedError

    def compute_baseline(self, x_s, y_s):
        raise NotImplementedError

    def compute_integral(self, x_s, y_s):
        raise NotImplementedError

    def compute(self, data, common):
        x_s, y_s = self.extract_data(data, common)
        return self.compute_integral(x_s, y_s)


class IntegrateFeatureEdgeBaseline(IntegrateFeature):
    """ A linear edge-to-edge baseline subtraction. """

    name = "Integral from baseline"

    @staticmethod
    def parameters():
        return (("Low limit", "Low limit for integration (inclusive)"),
                ("High limit", "High limit for integration (inclusive)"),
            )

    def compute_baseline(self, x, y):
        if np.any(np.isnan(y)):
            y, _ = nan_extend_edges_and_interpolate(x, y)
        return edge_baseline(x, y)

    def compute_integral(self, x, y_s):
        y_s = y_s - self.compute_baseline(x, y_s)
        if np.any(np.isnan(y_s)):
            # interpolate unknowns as trapz can not handle them
            y_s, _ = nan_extend_edges_and_interpolate(x, y_s)
        return np.trapz(y_s, x, axis=1)

    def compute_draw_info(self, x, ys):
        return [("curve", (x, self.compute_baseline(x, ys), INTEGRATE_DRAW_BASELINE_PENARGS)),
                ("curve", (x, ys, INTEGRATE_DRAW_BASELINE_PENARGS)),
                ("fill", ((x, self.compute_baseline(x, ys)), (x, ys)))]


class IntegrateFeatureSimple(IntegrateFeatureEdgeBaseline):
    """ A simple y=0 integration on the provided data window. """

    name = "Integral from 0"

    def compute_baseline(self, x_s, y_s):
        return np.zeros(y_s.shape)


class IntegrateFeaturePeakEdgeBaseline(IntegrateFeature):
    """ The maximum baseline-subtracted peak height in the provided window. """

    name = "Peak from baseline"

    @staticmethod
    def parameters():
        return (("Low limit", "Low limit for integration (inclusive)"),
                ("High limit", "High limit for integration (inclusive)"),
            )

    def compute_baseline(self, x, y):
        return edge_baseline(x, y)

    def compute_integral(self, x_s, y_s):
        y_s = y_s - self.compute_baseline(x_s, y_s)
        if len(x_s) == 0:
            return np.zeros((y_s.shape[0],)) * np.nan
        return np.nanmax(y_s, axis=1)

    def compute_draw_info(self, x, ys):
        bs = self.compute_baseline(x, ys)
        im = np.nanargmax(ys-bs, axis=1)
        lines = (x[im], bs[np.arange(bs.shape[0]), im]), (x[im], ys[np.arange(ys.shape[0]), im])
        return [("curve", (x, self.compute_baseline(x, ys), INTEGRATE_DRAW_BASELINE_PENARGS)),
                ("curve", (x, ys, INTEGRATE_DRAW_BASELINE_PENARGS)),
                ("line", lines)]


class IntegrateFeaturePeakSimple(IntegrateFeaturePeakEdgeBaseline):
    """ The maximum peak height in the provided data window. """

    name = "Peak from 0"

    def compute_baseline(self, x_s, y_s):
        return np.zeros(y_s.shape)


class IntegrateFeaturePeakXEdgeBaseline(IntegrateFeature):
    """ The X-value of the maximum baseline-subtracted peak height in the provided window. """

    name = "X-value of maximum from baseline"

    @staticmethod
    def parameters():
        return (("Low limit", "Low limit for integration (inclusive)"),
                ("High limit", "High limit for integration (inclusive)"),
            )

    def compute_baseline(self, x, y):
        return edge_baseline(x, y)

    def compute_integral(self, x_s, y_s):
        y_s = y_s - self.compute_baseline(x_s, y_s)
        if len(x_s) == 0:
            return np.zeros((y_s.shape[0],)) * np.nan
        # avoid whole nan rows
        whole_nan_rows = np.isnan(y_s).all(axis=1)
        y_s[whole_nan_rows] = 0
        # select positions
        pos = x_s[np.nanargmax(y_s, axis=1)]
        # set unknown results
        pos[whole_nan_rows] = np.nan
        return pos

    def compute_draw_info(self, x, ys):
        bs = self.compute_baseline(x, ys)
        im = np.nanargmax(ys-bs, axis=1)
        lines = (x[im], bs[np.arange(bs.shape[0]), im]), (x[im], ys[np.arange(ys.shape[0]), im])
        return [("curve", (x, self.compute_baseline(x, ys), INTEGRATE_DRAW_BASELINE_PENARGS)),
                ("curve", (x, ys, INTEGRATE_DRAW_BASELINE_PENARGS)),
                ("line", lines)]


class IntegrateFeaturePeakXSimple(IntegrateFeaturePeakXEdgeBaseline):
    """ The X-value of the maximum peak height in the provided data window. """

    name = "X-value of maximum from 0"

    def compute_baseline(self, x_s, y_s):
        return np.zeros(y_s.shape)


class IntegrateFeatureAtPeak(IntegrateFeature):
    """ Find the closest x and return the value there. """

    name = "Closest value"

    @staticmethod
    def parameters():
        return (("Closest to", "Nearest value"),
            )

    def extract_data(self, data, common):
        data, x, x_sorter = common
        return x, data.X

    def compute_baseline(self, x, y):
        return np.zeros(y.shape)

    def compute_integral(self, x_s, y_s):
        if len(x_s) == 0:
            return np.zeros((y_s.shape[0],)) * np.nan
        closer = np.nanargmin(abs(x_s - self.limits[0]))
        return y_s[:, closer]

    def compute_draw_info(self, x, ys):
        bs = self.compute_baseline(x, ys)
        im = np.array([np.nanargmin(abs(x - self.limits[0]))])
        dx = [self.limits[0], self.limits[0]]
        dys = np.hstack((bs[:, im], ys[:, im]))
        return [("curve", (dx, dys, INTEGRATE_DRAW_EDGE_PENARGS)),  # line to value
                ("dot", (x[im], ys[:, im]))]


class _IntegrateCommon(CommonDomain):

    def transformed(self, data):
        x = getx(data)
        x_sorter = np.argsort(x)
        return data, x, x_sorter


class Integrate(Preprocess):

    INTEGRALS = [IntegrateFeatureSimple,
                 IntegrateFeatureEdgeBaseline,
                 IntegrateFeaturePeakSimple,
                 IntegrateFeaturePeakEdgeBaseline,
                 IntegrateFeatureAtPeak,
                 IntegrateFeaturePeakXSimple,
                 IntegrateFeaturePeakXEdgeBaseline]

    # Integration methods
    Simple, Baseline, PeakMax, PeakBaseline, PeakAt, PeakX, PeakXBaseline = INTEGRALS

    def __init__(self, methods=Baseline, limits=None, names=None, metas=False):
        self.methods = methods
        self.limits = limits
        self.names = names
        self.metas = metas

    def __call__(self, data):
        common = _IntegrateCommon(data.domain)
        atts = []
        if self.limits:
            methods = self.methods
            if not isinstance(methods, Iterable):
                methods = [methods] * len(self.limits)
            names = self.names
            if not names:
                names = [" - ".join("{0}".format(e) for e in l) for l in self.limits]
            # no names in data should be repeated
            used_names = [var.name for var in data.domain.variables + data.domain.metas]
            for i, n in enumerate(names):
                n = get_unique_names(used_names, n)
                names[i] = n
                used_names.append(n)
            for limits, method, name in zip(self.limits, methods, names):
                atts.append(Orange.data.ContinuousVariable(
                    name=name,
                    compute_value=method(limits, common)))
        if not self.metas:
            domain = Orange.data.Domain(atts, data.domain.class_vars,
                                        metas=data.domain.metas)
        else:
            domain = Orange.data.Domain(data.domain.attributes, data.domain.class_vars,
                                        metas=data.domain.metas + tuple(atts))
        return data.from_table(domain, data)
