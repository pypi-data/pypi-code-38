"""
    This module contains various classes to provide interchangable data types
    between the view classes
"""

from collections import namedtuple
from enum import Enum


class Point(namedtuple('Point', ['p', 'q'])):
    """Representation of a point in the P/Q-plane"""

    def __str__(self):
        return f'(p:{self.p}, q:{self.q})'


class LinearFunction:
    """Helper class to simplify the handling of the PWLs"""

    def __init__(self, halfspace, limits):
        self.slope = halfspace.slope
        self.offset = halfspace.offset
        self.t = (limits.q * halfspace.offset - self.slope * limits.p)
    # pylint: disable=invalid-name
    def f(self, p):
        """
            This function computes the PWL function for the input value p.

        Parameters
        ----------
        p: float
            The active power value for this linear function

        Returns
        -------
            The result of the linear curve equation for the input value:
                $\text{self.slope}*p + \text{self.t}$
        """
        return self.slope * p + self.t

    def f_1(self, q):
        """
            This function computes the inverse PWL function for the input
            value q.

            Parameters
            ----------
            q: float
                The reactive power value for this linear function.

            Returns
            -------
            The result of the linear curve equation for the input value:
                        $ (q - \text{self.t}) / \text{self.slope}$
        """

        return (q - self.t) / self.slope

    def intersect_with(self, other):
        """
            This function computes the intersection of this LinearFunction with
            the LinearFunction `other`.

            Parameters
            ----------
            other: LinearFunction
                The other LinearFunction we want to compute the intersection with.

            Returns
            -------
                Either None or a Point that represents the intersection of the two
                instances of LinearFunction
        """
        denominator = other.slope - self.slope
        if denominator == 0:
            return None
        p = (self.t - other.t) / denominator
        q = other.slope * p + other.t
        return Point(p, q)

    def __repr__(self):
        return f"<f(p)={self.slope}p + {self.t}, f(q) = " \
               f"(q - {self.t}) / {self.slope}>"


class AutoValue(Enum):
    """
        This class provides a base class for enum that have a predefined,
        readable string representation.
    """
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


class Axis(AutoValue):
    """
        This enum represents the two axes.
    """
    ACTIVE_POWER = 1
    REACTIVE_POWER = 2


class Bound(AutoValue):
    """
        This enum represents the two bounds of the reactive and active limits
        of a capability region.
    """
    MIN = 1
    MAX = 2


class Orientation(AutoValue):
    """
        This enum represents the four possibilities for halfspaces. These
        should only appear in pairs of two: {RIGHT, LEFT} x {TOP, BOTTOM}.
    """
    RIGHT = 1
    LEFT = 2
    TOP = 3
    BOTTOM = 4
