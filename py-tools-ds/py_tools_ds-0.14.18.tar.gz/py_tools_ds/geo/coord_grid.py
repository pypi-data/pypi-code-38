# -*- coding: utf-8 -*-

import numpy as np
from shapely.geometry import box
from shapely.geometry import Polygon  # noqa F401  # flake8 issue
from typing import Sequence, Tuple, Union  # noqa F401  # flake8 issue

from ..numeric.vector import find_nearest
from .coord_calc import get_corner_coordinates

__author__ = "Daniel Scheffler"


def get_coord_grid(ULxy, LRxy, out_resXY):
    # type: (Sequence[float, float], Sequence[float, float], Sequence[float, float]) -> np.ndarray
    X_vec = np.arange(ULxy[0], LRxy[0], out_resXY[0])
    Y_vec = np.arange(ULxy[1], LRxy[1], out_resXY[1])

    # noinspection PyTypeChecker
    return np.meshgrid(X_vec, Y_vec)


def snap_bounds_to_pixGrid(bounds, gt, roundAlg='auto'):
    # type: (Sequence[float], Sequence[float], str) -> Tuple[float, float, float, float]
    """Snaps the given bounds to the given grid (defined by gt) under the use of the given round algorithm.
    NOTE: asserts equal projections of source and target grid

    :param bounds:      <tuple, list> (xmin, ymin, xmax, ymax)
    :param gt:          <tuple, list> GDAL geotransform
    :param roundAlg:    <str> 'auto', 'on', 'off'
    :return:
    """
    in_xmin, in_ymin, in_xmax, in_ymax = bounds
    xgrid = np.arange(gt[0], gt[0] + 2 * gt[1], gt[1])
    ygrid = np.arange(gt[3], gt[3] + 2 * abs(gt[5]), abs(gt[5]))
    xmin = find_nearest(xgrid, in_xmin, roundAlg, extrapolate=True)
    ymax = find_nearest(ygrid, in_ymax, roundAlg, extrapolate=True)
    xmax = find_nearest(xgrid, in_xmax, roundAlg, extrapolate=True)
    ymin = find_nearest(ygrid, in_ymin, roundAlg, extrapolate=True)

    return xmin, ymin, xmax, ymax


def is_coord_grid_equal(gt, xgrid, ygrid, tolerance=0.):
    # type: (Sequence[float], Sequence[float], Sequence[float], float) -> bool
    """Checks if a given GeoTransform exactly matches the given X/Y grid.

    :param gt:          GDAL GeoTransform
    :param xgrid:       numpy array defining the coordinate grid in x-direction
    :param ygrid:       numpy array defining the coordinate grid in y-direction
    :param tolerance:   float value defining a tolerance, e.g. 1e-8
    :return:
    """
    ULx, xgsd, holder, ULy, holder, ygsd = gt
    if all([is_point_on_grid((ULx, ULy), xgrid, ygrid, tolerance),
            abs(xgsd - abs(xgrid[1] - xgrid[0])) <= tolerance,
            abs(abs(ygsd) - abs(ygrid[1] - ygrid[0])) <= tolerance]):
        return True
    else:
        return False


def is_point_on_grid(pointXY, xgrid, ygrid, tolerance=0.):
    # type: (Sequence[float, float], Sequence[float], Sequence[float], float) -> bool
    """Checks if a given point is exactly on the given coordinate grid.

    :param pointXY:     (X,Y) coordinates of the point to check
    :param xgrid:       numpy array defining the coordinate grid in x-direction
    :param ygrid:       numpy array defining the coordinate grid in y-direction
    :param tolerance:   float value defining a tolerance, e.g. 1e-8
    """
    if abs(find_nearest(xgrid, pointXY[0], extrapolate=True) - pointXY[0]) <= tolerance and \
            abs(find_nearest(ygrid, pointXY[1], extrapolate=True) - pointXY[1]) <= tolerance:
        return True
    else:
        return False


def find_nearest_grid_coord(valXY, gt, rows, cols, direction='NW', extrapolate=True):
    # type: (Sequence[float, float], Sequence[float], int, int, str, bool) -> Tuple[float, float]
    UL, LL, LR, UR = get_corner_coordinates(gt=gt, rows=rows, cols=cols)  # (x,y) tuples
    round_x = {'NW': 'off', 'NO': 'on', 'SW': 'off', 'SE': 'on'}[direction]
    round_y = {'NW': 'on', 'NO': 'on', 'SW': 'off', 'SE': 'off'}[direction]
    tgt_xgrid = np.arange(UL[0], UR[0] + gt[1], gt[1])
    tgt_ygrid = np.arange(LL[1], UL[1] + abs(gt[5]), abs(gt[5]))
    tgt_x = find_nearest(tgt_xgrid, valXY[0], roundAlg=round_x, extrapolate=extrapolate)
    tgt_y = find_nearest(tgt_ygrid, valXY[1], roundAlg=round_y, extrapolate=extrapolate)

    return tgt_x, tgt_y


def move_shapelyPoly_to_image_grid(shapelyPoly, gt, rows, cols, moving_dir='NW'):
    # type: (Union[Polygon, box], Sequence[float], int, int, str) -> box
    polyULxy = (min(shapelyPoly.exterior.coords.xy[0]), max(shapelyPoly.exterior.coords.xy[1]))
    polyLRxy = (max(shapelyPoly.exterior.coords.xy[0]), min(shapelyPoly.exterior.coords.xy[1]))
    UL, LL, LR, UR = get_corner_coordinates(gt=gt, rows=rows, cols=cols)  # (x,y)
    round_x = {'NW': 'off', 'NO': 'on', 'SW': 'off', 'SE': 'on'}[moving_dir]
    round_y = {'NW': 'on', 'NO': 'on', 'SW': 'off', 'SE': 'off'}[moving_dir]
    tgt_xgrid = np.arange(UL[0], UR[0] + gt[1], gt[1])
    tgt_ygrid = np.arange(LL[1], UL[1] + abs(gt[5]), abs(gt[5]))
    tgt_xmin = find_nearest(tgt_xgrid, polyULxy[0], roundAlg=round_x, extrapolate=True)
    tgt_xmax = find_nearest(tgt_xgrid, polyLRxy[0], roundAlg=round_x, extrapolate=True)
    tgt_ymin = find_nearest(tgt_ygrid, polyLRxy[1], roundAlg=round_y, extrapolate=True)
    tgt_ymax = find_nearest(tgt_ygrid, polyULxy[1], roundAlg=round_y, extrapolate=True)

    return box(tgt_xmin, tgt_ymin, tgt_xmax, tgt_ymax)
