"""test_ulogconv."""
from context import mathpandas as mpd
import pandas as pd
import numpy as np
from numpy.testing import assert_almost_equal


def test_norm_2d():
    """test pythagoras series."""
    x = pd.Series([1, 2, 3, 4])
    y = pd.Series([2, 3, 4, 5])

    r = mpd.get_series_norm_2d(x, y, "test")

    assert_almost_equal(r.iloc[0], 2.23606797749979)
    assert_almost_equal(r.iloc[1], 3.605551275463989)
    assert_almost_equal(r.iloc[2], 5.0)
    assert_almost_equal(r.iloc[3], 6.4031242374328485)
    assert r.name == "test_norm"


def test_tilt_from_attitude():
    """test tilt series."""
    q0 = pd.Series([1])  # w
    q1 = pd.Series([0])  # x
    q2 = pd.Series([0])  # y
    q3 = pd.Series([0])  # z

    tilt = mpd.get_tilt_from_attitude(q0, q1, q2, q3, "angle_z_xy")
    assert_almost_equal(tilt, [0])

    q0 = pd.Series([0.707])
    q1 = pd.Series([0.707])
    q2 = pd.Series([0])
    q3 = pd.Series([0])

    tilt = mpd.get_tilt_from_attitude(q0, q1, q2, q3, "angle_z_xy")
    assert_almost_equal(tilt, [np.pi / 2.0])  # should be 90

    q0 = pd.Series([0.707])
    q1 = pd.Series([0])
    q2 = pd.Series([0.707])
    q3 = pd.Series([0])

    tilt = mpd.get_tilt_from_attitude(q0, q1, q2, q3, "angle_z_xy")
    assert_almost_equal(tilt, [np.pi / 2.0])  # should be 90


def test_heading_from_2d():
    """test heading from 2d."""
    # point north
    n = pd.Series([1])
    e = pd.Series([0])
    heading = mpd.get_heading_from_2d_vector(n, e)
    assert_almost_equal(heading, [0])

    # point east
    n = pd.Series([0])
    e = pd.Series([1])
    heading = mpd.get_heading_from_2d_vector(n, e)
    assert_almost_equal(heading, [np.pi / 2.0])

    # point north west 45
    n = pd.Series([1])
    e = pd.Series([-1])
    heading = mpd.get_heading_from_2d_vector(n, e)
    print(heading)
    assert_almost_equal(heading, [-0.78539816339])

    # point north east 45
    n = pd.Series([1])
    e = pd.Series([1])
    heading = mpd.get_heading_from_2d_vector(n, e)
    print(heading)
    assert_almost_equal(heading, [0.78539816339])
