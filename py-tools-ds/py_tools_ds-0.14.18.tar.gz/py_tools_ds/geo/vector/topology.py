# -*- coding: utf-8 -*-

import math
import warnings
import numpy as np
from typing import Union  # noqa F401  # flake8 issue

from geopandas import GeoDataFrame
from shapely.geometry import shape, Polygon, box, Point
from shapely.geometry import MultiPolygon  # noqa F401  # flake8 issue
from ..coord_trafo import mapYX2imYX
from ..coord_grid import find_nearest_grid_coord

__author__ = "Daniel Scheffler"


def get_overlap_polygon(poly1, poly2, v=False):
    """ Return a dict with the overlap of two shapely.Polygon() objects, the overlap percentage and the overlap area.

    :param poly1:   first shapely.Polygon() object
    :param poly2:   second shapely.Polygon() object
    :param v:       verbose mode
    :return:        overlap polygon as shapely.Polygon() object
    :return:        overlap percentage as float value [%]
    :return:        area of overlap polygon
    """
    # compute overlap polygon
    overlap_poly = poly1.intersection(poly2)
    if overlap_poly.geom_type == 'GeometryCollection':
        overlap_poly = overlap_poly.buffer(0)  # converts 'GeometryCollection' to 'MultiPolygon'

    if not overlap_poly.is_empty:
        # check if output is MultiPolygon or GeometryCollection -> if yes, convert to Polygon
        if overlap_poly.geom_type == 'MultiPolygon':
            overlap_poly = fill_holes_within_poly(overlap_poly)
        assert overlap_poly.geom_type == 'Polygon', \
            "get_overlap_polygon() did not return geometry type 'Polygon' but %s." % overlap_poly.geom_type

        overlap_percentage = 100 * shape(overlap_poly).area / shape(poly2).area
        if v:
            print('%.2f percent of the image to be shifted is covered by the reference image.' % overlap_percentage)
        return {'overlap poly': overlap_poly, 'overlap percentage': overlap_percentage,
                'overlap area': overlap_poly.area}
    else:
        return {'overlap poly': None, 'overlap percentage': 0, 'overlap area': 0}


def get_footprint_polygon(CornerLonLat, fix_invalid=False):
    """ Convert a list of coordinates into a shapely polygon object.

    :param CornerLonLat:    a list of coordinate tuples like [[lon,lat], [lon. lat], ..]
                            in clockwise or counter clockwise order
    :param fix_invalid:     fix invalid output polygon by returning its convex hull (somtimes this can be different)
    :return:                a shapely.Polygon() object
    """

    if fix_invalid:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')  # FIXME not working
            outpoly = Polygon(CornerLonLat)

            if not outpoly.is_valid:
                outpoly = outpoly.convex_hull
    else:
        outpoly = Polygon(CornerLonLat)

    assert outpoly.is_valid, 'The given coordinates result in an invalid polygon. Check coordinate order.' \
                             'Got coordinates %s.' % CornerLonLat
    return outpoly


def get_smallest_boxImYX_that_contains_boxMapYX(box_mapYX, gt_im, tolerance_ndigits=5):
    """Return image coordinates of the smallest box at the given coordinate grid that contains the given map coords box.

    :param box_mapYX:           input box ccordinates as YX-tuples
    :param gt_im:               geotransform of input box
    :param tolerance_ndigits:   tolerance to avoid that output image coordinates are rounded to next integer although
                                they have been very close to an integer before (this avoids float rounding issues)
                                -> tolerance is given as number of decimal digits of an image coordinate
    :return:
    """
    xmin, ymin, xmax, ymax = Polygon([(i[1], i[0]) for i in box_mapYX]).bounds  # map-bounds box_mapYX
    (ymin, xmin), (ymax, xmax) = mapYX2imYX([ymin, xmin], gt_im), mapYX2imYX([ymax, xmax], gt_im)  # image coord bounds

    # round min coords off and max coords on but tolerate differences below n decimal digits as the integer itself
    xmin, ymin, xmax, ymax = np.round([xmin, ymin, xmax, ymax], tolerance_ndigits)
    xmin, ymin, xmax, ymax = int(xmin), math.ceil(ymin), math.ceil(xmax), int(ymax)

    return (ymax, xmin), (ymax, xmax), (ymin, xmax), (ymin, xmin)  # UL_YX,UR_YX,LR_YX,LL_YX


def get_largest_onGridPoly_within_poly(outerPoly, gt, rows, cols):
    oP_xmin, oP_ymin, oP_xmax, oP_ymax = outerPoly.bounds
    xmin, ymax = find_nearest_grid_coord((oP_xmin, oP_ymax), gt, rows, cols, direction='SE')
    xmax, ymin = find_nearest_grid_coord((oP_xmax, oP_ymin), gt, rows, cols, direction='NW')
    return box(xmin, ymin, xmax, ymax)


def get_smallest_shapelyImPolyOnGrid_that_contains_shapelyImPoly(shapelyPoly):
    """Return the smallest box that matches the coordinate grid of the given geotransform.
    The returned shapely polygon contains image coordinates."""
    xmin, ymin, xmax, ymax = shapelyPoly.bounds  # image_coords-bounds

    return box(int(xmin), int(ymin), math.ceil(xmax), math.ceil(ymax))  # round min coords off and max coords on


def find_line_intersection_point(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b): return a[0] * b[1] - a[1] * b[0]
    div = det(xdiff, ydiff)
    if div == 0:
        return None, None
    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


def polyVertices_outside_poly(inner_poly, outer_poly):
    """Check if a shapely polygon (inner_poly) contains vertices that do not intersect another polygon (outer_poly)

    :param inner_poly: the polygon with the vertices to check
    :param outer_poly: the polygon where all vertices have to be inside
    """

    if inner_poly.within(outer_poly):
        # all vertices are inside outer_poly
        return False
    elif inner_poly.intersects(outer_poly):
        # check if all vertices intersect with outer poly
        GDF = GeoDataFrame(np.swapaxes(np.array(inner_poly.exterior.coords.xy), 0, 1), columns=['X', 'Y'])
        return False in GDF.apply(lambda GDF_row: Point(GDF_row.X, GDF_row.Y).intersects(outer_poly), axis=1).values
    else:
        # inner_poly does not intersect out_poly -> all vertices are outside
        return True


def fill_holes_within_poly(poly):
    # type: (Union[Polygon, MultiPolygon]) -> Polygon
    """Fill the holes within a shapely Polygon or MultiPolygon and returns a Polygon with only the outer boundary.

    :param poly:  <shapely.geometry.Polygon, shapely.geometry.MultiPolygon>, shapely.geometry.GeometryCollection>
    :return:
    """
    if poly.geom_type not in ['Polygon', 'MultiPolygon']:
        raise ValueError("Unexpected geometry type %s." % poly.geom_type)

    if poly.geom_type == 'Polygon':
        # return only the exterior polygon
        filled_poly = Polygon(poly.exterior)

    else:  # 'MultiPolygon'
        gdf = GeoDataFrame(columns=['geometry'])
        gdf['geometry'] = poly

        # get the area of each polygon of the multipolygon EXCLUDING the gaps in it
        gdf['area_filled'] = gdf.apply(
            lambda GDF_row: Polygon(np.swapaxes(np.array(GDF_row.geometry.exterior.coords.xy), 0, 1)).area, axis=1)

        largest_poly_filled = gdf.loc[gdf['area_filled'].idxmax()]['geometry']

        # return the outer boundary of the largest polygon
        filled_poly = Polygon(np.swapaxes(np.array(largest_poly_filled.exterior.coords.xy), 0, 1))

    return filled_poly
