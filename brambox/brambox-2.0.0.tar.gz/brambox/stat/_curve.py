#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Statistics on curves
#
import logging
import numpy as np
from scipy import interpolate, integrate

__all__ = ['auc', 'peak', 'point', 'threshold']
log = logging.getLogger(__name__)


def auc(curve):
    """ Computes the area under the curve.

    Args:
        curve (pandas.DataFrame): dataframe containing the X- and Y-values of the curve

    Returns:
        Number: Area under the curve

    Note:
        This function works under the assumption that the Y-axis values are on the first column and the X-axis on the second.
        After sorting the curve based on an increasing X-axis, this function will add a first point **(0, y[0])** and a last point **(x[-1], 0)**
        and then compute the integral using the trapezoid rule between all the points on the curve.
    """
    yaxis = curve.columns[0]
    xaxis = curve.columns[1]

    if len(curve) == 0:
        return float('nan')

    if len(curve) == 1:
        curve = curve.loc[0]
        return curve[xaxis] * curve[yaxis]

    if not curve[xaxis].is_monotonic_increasing:
        log.warning('Curve x-values are not sorted in increasing order. Sorting the values might not give correct results if there are multiple points with the same x value!')
        curve = curve.sort_values(xaxis)

    x = curve[xaxis].values
    y = curve[yaxis].values

    # Add first and last point
    x = np.insert(x, 0, 0)
    y = np.insert(y, 0, y[0])
    x = np.append(x, x[-1])
    y = np.append(y, 0)

    return integrate.trapz(y, x)


def peak(det, curve, maximum=True):
    """ Find the min/max Y-value on a curve and compute the detection threshold that matches it.

    Args:
        det (pandas.DataFrame): brambox dataframe with detections
        curve (pandas.DataFrame): dataframe containing the X- and Y-values of the curve
        maximum (boolean, optional): Whether to search for the maximum or minimum value; Default **True**

    Returns:
        tuple (number, row): Detection threshold and curve point that matches the value

    Note:
        This function works under the assumption that the Y-axis values are on the first column and the X-axis on the second.
        It also only works for curves where a decreasing detection threshold generates points in an increasing manner on the X-axis (e.g. PR, MR-FPPI).
    """
    yaxis = curve.columns[0]
    xaxis = curve.columns[1]

    # Sort curve by x axis and detections by confidence
    if not curve[xaxis].is_monotonic_increasing:
        curve = curve.sort_values(xaxis)
    if not det.confidence.is_monotonic_decreasing:
        det = det.sort_values('confidence', ascending=False)

    # Get correct position on curve
    if maximum:
        pt = curve[yaxis].idxmax()
    else:
        pt = curve[yaxis].idxmin()
    iloc = curve.index.get_loc(pt)

    # Get detection threshold
    det = det.loc[~det.confidence.duplicated(keep='last')]      # Only keep last point where detection confidence is the same
    threshold = det['confidence'].iat[iloc]
    return threshold, curve.iloc[iloc]


def point(det, curve, threshold):
    """ Return the point on the curve that matches the given detection threshold.

    Args:

    Returns:
        tuple (number, row): Actual detection threshold and curve point that matches the threshold

    Note:
        This function works under the assumption that the Y-axis values are on the first column and the X-axis on the second.
        It also only works for curves where a decreasing detection threshold generates points in an increasing manner on the X-axis (e.g. PR, MR-FPPI).

    Warning:
        If there are no detections with a higher confidence than the given threshold, this function will return ``np.nan, None``.
    """
    xaxis = curve.columns[1]

    # Sort curve by x axis and detections by confidence
    if not curve[xaxis].is_monotonic_increasing:
        curve = curve.sort_values(xaxis)
    if not det.confidence.is_monotonic_decreasing:
        det = det.sort_values('confidence', ascending=False)

    # Get detection iloc of last detection >= threshold
    det = det[det.confidence >= threshold]
    if det.empty:
        return np.nan, None
    iloc = det.index.get_loc(det.index[-1])

    return det.confidence.iloc[-1], curve.iloc[iloc]


def threshold(det, curve, column, value, first=True):
    """ Compute the necessary detection threshold value to reach a certain value on the curve.

    Args:
        det (pandas.DataFrame): brambox dataframe with detections
        curve (pandas.DataFrame): dataframe containing the X- and Y-values of the curve
        column (string): On which axis to reach a threshold
        value (number): threshold value to reach on the curve
        first (boolean, optional): Whether to reach the first or last value bigger than the given value; Default **True**

    Returns:
        tuple (number, row): Detection threshold and curve point that matches the value

    Note:
        This function works under the assumption that the Y-axis values are on the first column and the X-axis on the second.
        It also only works for curves where a decreasing detection threshold generates points in an increasing manner on the X-axis (e.g. PR, MR-FPPI).

        It will sort the values based on the X-axis and then search for the matching point on the curve. |br|
        If `first` is **True**, the curve will find the first item greater or equal than the given value,
        otherwise the last. This only matters for the Y-axis values, where there can be multiple peaks.

    Warning:
        If the value is not found on the curve, this function will return ``np.nan, None``.
    """
    xaxis = curve.columns[1]

    # Sort curve by x axis and detections by confidence
    if not curve[xaxis].is_monotonic_increasing:
        curve = curve.sort_values(xaxis)
    if not det.confidence.is_monotonic_decreasing:
        det = det.sort_values('confidence', ascending=False)

    # Get correct position on curve
    threshold = curve[column] >= value
    if not threshold.any():
        return np.nan, None

    if first:
        iloc = curve.index.get_loc(curve[threshold].index[0])
    else:
        iloc = curve.index.get_loc(curve[threshold].index[-1])

    # Get detection threshold
    det = det.loc[~det.confidence.duplicated(keep='last')]      # Only keep last point where detection confidence is the same
    threshold = det['confidence'].iat[iloc]
    return threshold, curve.iloc[iloc]
