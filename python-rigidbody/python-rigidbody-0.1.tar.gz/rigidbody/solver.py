from typing import Optional

from .matrix import (Matrix, Vector)


def approx_jacobian(f, x: Vector, epsilon: Optional[float]=0.001):

    J = Matrix(x.rows, x.rows)
    fx = f(x)

    for row in range(x.rows):
        J[row, :] = (f(x + epsilon * Vector.e(x.rows, row)) - fx) / epsilon

    return J

