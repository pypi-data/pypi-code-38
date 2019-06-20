import numpy as np
from worker.data.operations import none_to_nan, is_number


def percentile(ls, percent):
    """
    Calculates percentile without considering np.nan and None values. Returns 0 is all values are np.nan or None
    :param ls:
    :param percent:
    :return:
    """
    try:
        p = np.nanpercentile(none_to_nan(ls), percent)
        if p >= 0 or p <= 0:
            return p

        return None
    except TypeError:
        return None


def mean_angles(ls):
    """
    to compute mean of list of angles
    :param ls: a list of angles
    :return: mean value of angles
    """
    x_mean = np.nanmean(np.cos(np.deg2rad(ls)))
    y_mean = np.nanmean(np.sin(np.deg2rad(ls)))
    mean_deg = np.rad2deg(np.arctan2(y_mean, x_mean))

    return mean_deg % 360


def angle_difference(ang1, ang2):
    """
    Code from: https://rosettacode.org/wiki/Angle_difference_between_two_bearings#Python
    :param ang1:
    :param ang2:
    :return:
    """
    if not is_number(ang1) or not is_number(ang2):
        return None

    r = (ang2 - ang1) % 360.0
    if r >= 180.0:
        r -= 360.0
    return r


def abs_angle_difference(ang1, ang2):
    """
    The absolute difference between two angles.
    :param ang1:
    :param ang2:
    :return:
    """
    diff = angle_difference(ang1, ang2)
    if is_number(diff):
        return abs(diff)

    return None


def split_zip_edges(arr, separation_length=1, min_segment_length=1):
    """
    In cases that you have elements and you want only values that are close to each other.
    :param arr: array of non-continuous data
    :param separation_length: separation length
    :param min_segment_length: min length of each segment
    :return: a list of tuples representing the start and stop of each segment
    """
    if isinstance(arr, list):
        arr = np.array(arr)

    m = np.concatenate(([True], arr[1:] > arr[:-1] + separation_length, [True]))
    idx = np.flatnonzero(m)
    ll = arr.tolist()
    return [(ll[i], ll[j - 1]) for i, j in zip(idx[:-1], idx[1:]) if (ll[j - 1] + 1 - ll[i]) >= min_segment_length]


def start_stop(arr, trigger_val, min_len_thresh=1):
    """
    If you have an array representing values and you only want
    the values which are equal to a specific trigger_value.
    Another param is the minimum of each interval size.
    :param arr: a continuous stream of data
    :param trigger_val: desired value
    :param min_len_thresh: the min distance between two separate segments
    :return: a list of tuples representing the start and stop of each segment
    """
    # "Enclose" mask with sentient to catch shifts later on
    mask = np.r_[False, np.equal(arr, trigger_val), False]

    # Get the shifting indices
    idx = np.flatnonzero(mask[1:] != mask[:-1])

    # Get lengths
    lens = idx[1::2] - idx[::2]

    res = idx.reshape(-1, 2)[lens >= min_len_thresh] - [0, 1]

    return [(i[0], i[-1]) for i in res]
