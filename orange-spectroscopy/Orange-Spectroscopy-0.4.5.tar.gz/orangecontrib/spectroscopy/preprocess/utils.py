import numpy as np
from Orange.data.util import SharedComputeValue
from scipy.interpolate import interp1d

from orangecontrib.spectroscopy.data import getx


def is_increasing(a):
    return np.all(np.diff(a) >= 0)


class PreprocessException(Exception):

    def message(self):
        if self.args:
            return self.args[0]
        else:
            return self.__class__.__name__


class MissingReferenceException(PreprocessException):
    pass


class WrongReferenceException(PreprocessException):
    pass


class SelectColumn(SharedComputeValue):

    def __init__(self, feature, commonfn):
        super().__init__(commonfn)
        self.feature = feature

    def compute(self, data, common):
        return common[:, self.feature]


class CommonDomain:
    """A utility class that helps constructing common transformation for
    SharedComputeValue features. It does the domain transformation
    (input domain needs to be the same as it was with training data).
    """
    def __init__(self, domain):
        self.domain = domain

    def __call__(self, data):
        data = self.transform_domain(data)
        return self.transformed(data)

    def transform_domain(self, data):
        if data.domain != self.domain:
            data = data.from_table(self.domain, data)
        return data

    def transformed(self, data):
        raise NotImplemented


class CommonDomainRef(CommonDomain):
    """CommonDomain which also ensures reference domain transformation"""
    def __init__(self, reference, domain):
        super().__init__(domain)
        self.reference = reference

    def interpolate_extend_to(self, interpolate, wavenumbers):
        """
        Interpolate data to given wavenumbers and extend the possibly
        nan-edges with the nearest values.
        """
        # interpolate reference to the given wavenumbers
        X = interp1d_with_unknowns_numpy(getx(interpolate), interpolate.X, wavenumbers)
        # we know that X is not NaN. same handling of reference as of X
        X, _ = nan_extend_edges_and_interpolate(wavenumbers, X)
        return X


class CommonDomainOrder(CommonDomain):
    """CommonDomain + it also handles wavenumber order.
    """
    def __call__(self, data):
        data = self.transform_domain(data)

        # order X by wavenumbers
        xs, xsind, mon, X = transform_to_sorted_features(data)
        xc = X.shape[1]

        # do the transformation
        X = self.transformed(X, xs[xsind])

        # restore order
        return self._restore_order(X, mon, xsind, xc)

    def _restore_order(self, X, mon, xsind, xc):
        # restore order and leave additional columns as they are
        restored = transform_back_to_features(xsind, mon, X[:, :xc])
        return np.hstack((restored, X[:, xc:]))

    def transformed(self, X, wavenumbers):
        raise NotImplemented


class CommonDomainOrderUnknowns(CommonDomainOrder):
    """CommonDomainOrder + it also handles unknown values: it interpolates
    values before computation and afterwards sets them back to unknown.
    """
    def __call__(self, data):
        data = self.transform_domain(data)

        # order X by wavenumbers
        xs, xsind, mon, X = transform_to_sorted_features(data)
        xc = X.shape[1]

        # interpolates unknowns
        X, nans = nan_extend_edges_and_interpolate(xs[xsind], X)

        # Replace remaining NaNs (where whole rows were NaN) with
        # with some values so that the function does not crash.
        # Results are going to be discarded later.
        X[np.isnan(X)] = 1.

        # do the transformation
        X = self.transformed(X, xs[xsind])

        # set NaNs where there were NaNs in the original array
        if nans is not None:
            # transformed can have additional columns
            addc = X.shape[1] - xc
            if addc:
                nans = np.hstack((nans, np.zeros((X.shape[0], addc), dtype=np.bool)))
            X[nans] = np.nan

        # restore order
        return self._restore_order(X, mon, xsind, xc)


def nan_extend_edges_and_interpolate(xs, X):
    """
    Handle NaNs at the edges are handled as with savgol_filter mode nearest:
    the edge values are interpolated. NaNs in the middle are interpolated
    so that they do not propagate.
    """
    nans = None
    if np.any(np.isnan(X)):
        nans = np.isnan(X)
        X = X.copy()
        xs, xsind, mon, X = transform_to_sorted_wavenumbers(xs, X)
        fill_edges(X)
        X = interp1d_with_unknowns_numpy(xs[xsind], X, xs[xsind])
        X = transform_back_to_features(xsind, mon, X)
    return X, nans


def transform_to_sorted_features(data):
    xs = getx(data)
    return transform_to_sorted_wavenumbers(xs, data.X)


def transform_to_sorted_wavenumbers(xs, X):
    xsind = np.argsort(xs)
    mon = is_increasing(xsind)
    X = X if mon else X[:, xsind]
    return xs, xsind, mon, X


def transform_back_to_features(xsind, mon, X):
    return X if mon else X[:, np.argsort(xsind)]


def fill_edges(mat):
    """Replace (inplace!) NaN at sides with the closest value"""
    for l in mat:
        loc = np.where(~np.isnan(l))[0]
        if len(loc):
            fi, li = loc[[0, -1]]
            l[:fi] = l[fi]
            l[li + 1:] = l[li]


def remove_whole_nan_ys(x, ys):
    """Remove whole NaN columns of ys with corresponding x coordinates."""
    whole_nan_columns = np.isnan(ys).all(axis=0)
    if np.any(whole_nan_columns):
        x = x[~whole_nan_columns]
        ys = ys[:, ~whole_nan_columns]
    return x, ys


def interp1d_with_unknowns_numpy(x, ys, points, kind="linear"):
    if kind != "linear":
        raise NotImplementedError
    out = np.zeros((len(ys), len(points)))*np.nan
    sorti = np.argsort(x)
    x = x[sorti]
    for i, y in enumerate(ys):
        y = y[sorti]
        nan = np.isnan(y)
        xt = x[~nan]
        yt = y[~nan]
        # do not interpolate unknowns at the edges
        if len(xt):  # check if all values are removed
            out[i] = np.interp(points, xt, yt, left=np.nan, right=np.nan)
    return out


def interp1d_with_unknowns_scipy(x, ys, points, kind="linear"):
    out = np.zeros((len(ys), len(points)))*np.nan
    sorti = np.argsort(x)
    x = x[sorti]
    for i, y in enumerate(ys):
        y = y[sorti]
        nan = np.isnan(y)
        xt = x[~nan]
        yt = y[~nan]
        if len(xt):  # check if all values are removed
            out[i] = interp1d(xt, yt, fill_value=np.nan, assume_sorted=True,
                              bounds_error=False, kind=kind, copy=False)(points)
    return out


def interp1d_wo_unknowns_scipy(x, ys, points, kind="linear"):
    return interp1d(x, ys, fill_value=np.nan, kind=kind, bounds_error=False)(points)


def edge_baseline(x, y):
    """Baseline from edges. Assumes data without NaNs"""
    return linear_baseline(x, y, zero_points=[x[0], x[-1]]) if len(x) else 0


def linear_baseline(x, y, zero_points=None):
    values_zero_points = interp1d(x, y, axis=1, fill_value="extrapolate")(zero_points)
    return interp1d(zero_points, values_zero_points, axis=1, fill_value="extrapolate")(x)


def replace_infs(array):
    """ Replaces inf and -inf with nan.
    This should be used anywhere a divide-by-zero can happen (/, np.log10, etc)"""
    array[np.isinf(array)] = np.nan
    return array
