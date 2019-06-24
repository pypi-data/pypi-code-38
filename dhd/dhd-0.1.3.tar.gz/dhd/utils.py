from shapely.geometry import LineString
import numpy as np


def reverse_linestring(line):
    """
    Reverse the coordinates orded of a LineString.

    Parameters
    ----------
    line: LineString
        LineString to reverse.

    Returns
    -------
    LineString
        Reversed LineString.
    """

    x, y = line.xy
    x.reverse()
    y.reverse()

    return LineString([(a, b) for a, b in zip(x, y)])


def distance(p1, p2):
    """
    Function to compute the euclidean distance between the points *p1* and *p2*.

    Parameters
    ----------
    p1: tuple
        Coordinates of the first point.
    p2: tuple
        Coordinates of the second point.

    Returns
    -------
    float
        Distance between *p1* and *p2*.
    """

    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def get_list_transpose(list):
    """
    Take the transpose of a list of tuples.

    Parameters
    ----------
    list: list
        List of tuples. Ex. [(1,2),(2,3),(3,4)].

    Returns
    -------
    list
        Transpose of the list. Ex [[1,2,3],[2,3,4]].
    """

    verso = [[], []]
    for x, y in list:
        verso[0].append(x)
        verso[1].append(y)

    return verso


def get_moment(data, n):
    """
    Compute the *n* moment of the data list *data*.

    Parameters
    ----------
    data: list
        Data to take the moment of.
    n: int
        Moment number.

    Returns
    -------
    float
        *n* moment of the data.
    """

    N = len(data)
    m_n = 0
    for x in data:
        m_n += x ** n

    m_n /= N

    return m_n


def normalized_inner_product(x, y):
    """
    Compute the inner product of two vectors and divide by the product of their
    lengths, namely the cosine of the angle between them.

    Parameters
    ----------
    x: numpy.array
        First vector.
    y: numpy.array
        Second vector.

    Returns
    -------
    float
        Cosine of the angle between the two vectors.
    """

    N = np.sqrt(np.dot(x, x) * np.dot(y, y))

    return np.dot(x, y) / N
