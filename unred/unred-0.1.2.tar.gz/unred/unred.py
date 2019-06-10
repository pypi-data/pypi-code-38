"""
For observed colors of stars and their theoretical path
calculate color excess and extinction.

"""
import numpy as np
from scipy.optimize import fsolve


def _read_file(filename, data_type):
    try:
        with open(filename, 'r') as file_descriptor:
            file_content = np.loadtxt(file_descriptor, data_type, ndmin=1)
    except FileNotFoundError:
        print("File {} doesn't exist!".format(filename))
        return

    return file_content


def read_unreddened_sequence(filename):
    """
    Read an unreddened sequence of stars from a text file.

    Parameters
    ----------
    filename : str
        The name (with a path if neccessary) of the file which
        contains two columns with floats. The first one represents
        X color, the second column - Y color. The data must
        be sorted by increasing temperature.

    Returns
    -------
    model : ndarray
        Data read from the text file.
    """
    data_type = {'names': ('x', 'y'), 'formats': ('f8', 'f8')}
    model = _read_file(filename, data_type)

    return model


def read_reddened_stars(filename):
    """
    Read reddened stars from a text file.

    Parameters
    ----------
    filename : str
        The name (with a path if neccessary) of the file which
        has 5 five columns. The first one with integers, the rest
        with floats. Each column represents: star_id, x_color, y_color,
        x_color_error, y_color_error.

    Returns
    -------
    stars : ndarray
        Data read from the text file.
    """
    data_type = {'names': ('id', 'x', 'y', 'xerr', 'yerr'),
                 'formats': ('i8', 'f8', 'f8', 'f8', 'f8')}
    stars = _read_file(filename, data_type)

    return stars


def unreddened_sequence_nodes(point, unreddened_sequence, reddening_line_slope):
    """
    Determine an index(es) of the n-th point(s) of the unreddened sequence
    for the given point P(x, y). n-th and n+1-th points set a segment
    which intersects with the reddening line passing through P.

    Parameters
    ----------
    point : tuple
        A tuple containing xy coordinates (float) on the color-color plane.
    unreddened_sequence : ndarray
        A model of the unreddened sequence on the color-color plane.
    reddening_line_slope : float
        A value of a slope of the reddening line.
        For example E(U-B)/E(B-V) = 0.72.

    Returns
    -------
    nodes_list : list
        A list of an index(es).
    """
    nodes_list = []

    for node, sequence_piece in (
            enumerate(zip(unreddened_sequence, unreddened_sequence[1:]))):

        if point[0] <= sequence_piece[0][0]:
            continue
        else:
            first_differential_slope = (
                slope_line(point, sequence_piece[0]) - reddening_line_slope)
            second_differential_slope = (
                slope_line(point, sequence_piece[1]) - reddening_line_slope)

            if first_differential_slope*second_differential_slope < 0:
                nodes_list += [node]

    return nodes_list


def slope_line(first_point, second_point):
    """
    Calculate a value of a line slope for the given two points.

    Parameters
    ----------
    first_point, second_point : tuple
        A tuple containing xy coordinates (float) on the color-color plane.

    Returns
    -------
    slope : float
        A value of the slope line.
    """
    slope = (second_point[1] - first_point[1])
    slope /= (second_point[0] - first_point[0])

    return slope


def y_intercept_line(slope, point):
    """
    Calculate a y-intercept of a line for given values of slope and point.

    Parameters
    ----------
    slope : float
        A value of slope line.
    point : tuple
        A tuple with xy coordinates.

    Returns
    -------
    y-intercept : float
        A vaule of the y-intercept for the line.
    """
    return point[1] - slope*point[0]


def interpolation_line_coefficients(unreddened_sequence, sequence_nodes):
    """
    Calculate coefficients of straight lines of which an unreddened stars
    sequence is built. The coefficients are calculated only for lines
    passing through sequence nodes and their next nodes.

    Parameters
    ----------
    unreddened_sequence : ndarray
        A value retured by the read_unreddened_sequence() function.
    sequence_nodes : list
        A value retured by the unreddened_sequence_nodes() function.

    Returns
    -------
    coefficients : tuple
        A tuple containing tuples. Each nested tuple has two
        coefficients of a single straight line.
    """
    coefficients = ()

    for node in sequence_nodes:
        A = slope_line(unreddened_sequence[node+1], unreddened_sequence[node])
        B = y_intercept_line(A, unreddened_sequence[node])
        coefficients += (A, B),

    return coefficients


def line(coefficients, x):
    """
    For a given value x calculate y = A*x + B.

    Parameters
    ----------
    coefficients : tuple
        A tuple with the line coefficients (A, B).
    x : float
        An argument of a linear equation.

    Returns
    -------
    y : float
        A calculated value of the linear equation.
    """
    return coefficients[0]*x + coefficients[1]


def find_intersection(first_line, second_line):
    """
    Find x value of common point for two crossing lines.

    Parameters
    ----------
    first_line, second_line : tuple
        A tuple with the line coefficients (A, B).

    Returns
    -------
    x : float
        An x coordinate of the point which belongs to both lines.
    """
    return fsolve(lambda x: line(first_line, x) - line(second_line, x), 0.0)


def point_positions(point):
    """
    Iterate point positions.

    Parameters
    ----------
    point : tuple
        A tuple made of id, x, y, dx, dy.

    Returns
    -------
    x, y : tuple
        All combinations of a pair (X,Y) where
        X = x/x-dx/x+dx, Y = y/y-dy/y+dy
    """
    x, y = point[1], point[2]
    dx, dy = point[3], point[4]

    for x_position in (x, x - dx, x + dx):
        for y_position in (y, y - dy, y + dy):
            yield x_position, y_position


def extinction(stars, unreddened_sequence, reddening_line_slope,
               extinction_parameter):
    """
    Assuming that stars come from the unreddened_sequence calculate
    color excess and extinction knowing the reddening_line_slope and
    extinction_parameter.

    Parameters
    ----------
    stars : ndarray
        See the read_reddened_stars function.
    unreddened_sequence : ndarray
        See the read_unreddened_sequence function.
    reddening_line_slope : float
        A value defining a slope of the reddening line.
    extinction_parameter : float
        A ratio of total to selective extinction.

    Returns
    -------
    extinction_values : list of tuples
        Each tuple containing:
        - star id
        - xy position of a star (x_color, y_color)
        - xy position of a star without extinction (x0_color, y0_color)
        - color excess (E(x_color), E(y_color))
        - extinction

        For one star can be more than one calculated value of extinction.
        See the point_positions iterator to understand why.
    """
    extinction_values = []

    for star in stars:
        star_id = star[0]
        point_positions_iterator = point_positions(star)

        for point_coordinates in point_positions_iterator:
                nodes = unreddened_sequence_nodes(
                    point_coordinates,
                    unreddened_sequence,
                    reddening_line_slope)
                line_coefficients = interpolation_line_coefficients(
                    unreddened_sequence, nodes)
                parrallel_line_coefficients = (
                    reddening_line_slope,
                    y_intercept_line(reddening_line_slope, point_coordinates))

                for i, node in enumerate(nodes):
                    intersect_x0 = find_intersection(
                        line_coefficients[i], parrallel_line_coefficients)
                    intersect_y0 = line(
                        parrallel_line_coefficients, intersect_x0)
                    x_excess = point_coordinates[0] - float(intersect_x0)
                    y_excess = point_coordinates[1] - float(intersect_y0)
                    extinction = extinction_parameter*x_excess
                    output = (star_id,
                              point_coordinates[0], point_coordinates[1],
                              float(intersect_x0), float(intersect_y0),
                              x_excess, y_excess, extinction)

                    extinction_values += [output]

    return extinction_values


def select_extinction(extinction, way="min"):
    """
    For each star sort and select only one extinction value.

    Parameters
    ----------
    extinction : list of tuples
        A list returned by the extinction function.
    way : string
        A method to select only one extinction value.
        - "min"
        - "max"

        Default value "min".
    """
    stars_indexes = set([star[0] for star in extinction])
    extinction_values = []

    for star_id in stars_indexes:
        star_extinction = []

        for ext in extinction:
            if star_id == ext[0]:
                star_extinction += [ext]

        if way == "min":
            extinction_values += [min(star_extinction, key=lambda x: x[-1])]
        else:
            extinction_values += [max(star_extinction, key=lambda x: x[-1])]

    return extinction_values


def print_header():
    """
    Print a header of the output.
    """
    print("# ID x_ci y_ci x_ci0 y_ci0 E(x_ci) E(y_ci) A")


def print_extinction(extinction):
    """
    Print formatted output.

    Parameters
    ----------
    extinction : list of tuples
        A list returned by the extinction function.
    """
    string_format = "{0:4d} {1:7.4f} {2:7.4f} {3:7.4f} {4:7.4f}"
    string_format += " {5:8.4f} {6:7.4f} {7:8.4f}"
    print_header()

    for row in extinction:
        print(string_format.format(*row))
