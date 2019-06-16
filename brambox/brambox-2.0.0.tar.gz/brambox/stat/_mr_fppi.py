#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#
#   Functions for generating Miss rate vs FPPI curve values and calculating log average miss rate
#
import numpy as np
import pandas as pd
from scipy import interpolate
from ..util import np_col
from ._matchboxes import match_det
from . import coordinates

__all__ = ['mr_fppi', 'lamr']


def mr_fppi(det, anno, threshold=0.5, ignore=True):
    """ Computes MR-FPPI-curve between detection and annotation dataframe.
    This function will match detections and annotations by computing the IoU.

    Args:
        det (pandas.DataFrame): Dataframe with detections
        anno (pandas.DataFrame): Dataframe with annotations
        threshold (number): Threshold to count a detection as true positive; Default **0.5**
        ignore (Boolean, optional): Whether to consider the ignore flag of annotations when matching detections; Default **True**

    Returns:
        pandas.Dataframe: DataFrame with 2 columns **('miss_rate', 'false_positives_per_image')** that has the points of the MR-FPPI-curve

    Note:
        If you want more control over the parameters to match detections (eg. Change the criteria to something else than IoU),
        you can call the :func:`brambox.stat.match_boxes` function yourself and provide other arguments. |br|
        This function will first check whether the detection dataframe has tp/fp columns and compute them otherwise.

    Note:
        If ignore is true, this function will match the detections using :func:`~brambox.stat.coordinates.pdollar` and set consider ignored annotations as regioned that can be matched to multiple times,
        otherwise it will use a regular :func:`~brambox.stat.coordinates.iou` and discard the ignored labels.
        If there are no ignored annotations, this boils down to the same.
    """
    # Compute TP/FP
    if not {'tp', 'fp'}.issubset(det.columns):
        crit = coordinates.pdollar if ignore else coordinates.iou
        label = len({*det.class_label.unique(), *anno.class_label.unique()}) > 1
        det = match_det(det, anno, threshold, criteria=crit, class_label=label, ignore='m' if ignore else 'n')
    elif not det.confidence.is_monotonic_decreasing:
        det = det.sort_values('confidence', ascending=False)

    # Compute MR FPPI
    num_images = len(anno.image.cat.categories)
    if ignore:
        num_annos = (~anno.ignore).sum()
    else:
        num_annos = len(anno.index)

    matches = det.loc[(det.tp | det.fp), ['tp', 'fp', 'confidence']]
    summed = matches[['tp', 'fp']].cumsum()
    mr = 1 - summed.tp / num_annos
    fppi = summed.fp / num_images

    mrfppi = pd.DataFrame({'miss_rate': mr, 'false_positives_per_image': fppi})
    mrfppi = mrfppi.loc[~matches.confidence.duplicated(keep='last')].reset_index(drop=True)     # Only keep last point where detection confidence is the same
    return mrfppi


def lamr(mr_fppi, samples=9):
    """ Computes log average miss-rate from a MR-FPPI-curve.

    The log average miss-rate is defined as the average of a number of evenly spaced log miss-rate samples
    on the :math:`{log}(FPPI)` axis within the range :math:`[10^{-2}, 10^{0}]`

    Args:
        mr_fppi (pandas.DataFrame): Miss-rate and FPPI values
        samples (int, optional): Number of samples within the given interval; Default **9**

    Returns:
        Number: log average miss-rate
    """
    if len(mr_fppi) <= 1:
        return float('nan')

    m = np_col(mr_fppi, 'miss_rate')
    f = np_col(mr_fppi, 'false_positives_per_image')

    s = np.logspace(-2., 0., samples)
    interpolated = interpolate.interp1d(f, m, fill_value=(1., 0.), bounds_error=False)(s)
    log_interpolated = np.log(interpolated)

    avg = sum(log_interpolated) / len(log_interpolated)
    return np.exp(avg)
