from typing import Optional

from .matrix import (Matrix, Vector)


def approx_jacobian(f, x: Vector, epsilon: Optional[float]=0.001):
    """ Returns the approximate Jacobian of a function

    :param f: a function of the form y = f(x)
    :param x: the point where the function is approximated
    :param epsilon: the step-size used to approximate the Jacobian

    :returns: a Matrix object

    """
    J = Matrix(x.rows, x.rows)
    fx = f(x)

    for row in range(x.rows):
        J[row, :] = (f(x + epsilon * Vector.e(x.rows, row)) - fx) / epsilon

    return J

